import pandas as pd
import numpy as np
import gdxtools as gt
import folium
from itertools import permutations
from scipy.spatial import Delaunay
from geopy.distance import geodesic


def create_circle_with_radius(lat, lng, radiusMiles):
    lat_ring = []
    lng_ring = []

    R = 3959  # radius of the earth (miles)

    step = 5
    for brng in range(0, 360+step, step):
        lat2 = np.arcsin(np.sin(lat * np.pi/180) * np.cos(radiusMiles / R) + np.cos(lat * np.pi/180)
                         * np.sin(radiusMiles / R) * np.cos(brng * np.pi/180))

        lng2 = lng * np.pi/180 + np.arctan2(np.sin(brng * np.pi/180) * np.sin(radiusMiles / R) * np.cos(lat * np.pi/180),
                                            np.cos(radiusMiles / R) - np.sin(lat * np.pi/180) * np.sin(lat2 * np.pi/180))

        lat_ring.append(lat2 * 180/np.pi)
        lng_ring.append(lng2 * 180/np.pi)

    return list(zip(lat_ring, lng_ring))


def create_transmission_network(geoPts):
    if not isinstance(geoPts, dict):
        raise Exception('geoPts must be a type dict and in format {region:(lat,lng)}')

    agg = pd.DataFrame.from_dict(geoPts, orient='index', columns=[
                                 'lat', 'lng']).reset_index(drop=False).copy()
    agg.rename(columns={'index': 'region'}, inplace=True)

    cir = create_circle_with_radius(lat=agg.lat.mean(),
                                    lng=agg.lng.mean(),
                                    radiusMiles=1.2 * max_network_distance(geoPts=geoPts))

    cir = dict(zip(['cir_'+str(n) for n, i in enumerate(cir)], cir))

    n_cir = pd.DataFrame.from_dict(data=cir, orient='index', columns=[
                                   'lat', 'lng']).reset_index(drop=False)
    n_cir.rename(columns={'index': 'region'}, inplace=True)

    a = agg.append(n_cir)

    triang = Delaunay(np.array(list(zip(a.lat, a.lng))), qhull_options='Qt')

    arcs = []
    perm = [arcs.extend(list(permutations(i, 2))) for i in triang.simplices]
    arcs = list(set(arcs))

    # remove circle nodes
    idx = [i for i, x in enumerate(a.region.values) if x.split('_')[0] == 'cir']
    cln_arcs = []
    for a, b in arcs:
        if a not in idx and b not in idx:
            cln_arcs.append((a, b))

    # map arcs index to region name
    arcs_lbl = [(agg.region[agg.index[i]], agg.region[agg.index[j]]) for i, j in cln_arcs]

    # create dataframe
    network = pd.DataFrame(index=range(len(cln_arcs)))
    network['from_lat'] = [agg.loc[i[0], 'lat'] for n, i in enumerate(cln_arcs)]
    network['from_lng'] = [agg.loc[i[0], 'lng'] for n, i in enumerate(cln_arcs)]
    network['to_lat'] = [agg.loc[i[1], 'lat'] for n, i in enumerate(cln_arcs)]
    network['to_lng'] = [agg.loc[i[1], 'lng'] for n, i in enumerate(cln_arcs)]

    network['miles'] = [geodesic(tuple([network.loc[i, 'from_lat'], network.loc[i, 'from_lng']]), tuple(
        [network.loc[i, 'to_lat'], network.loc[i, 'to_lng']])).miles for i in range(len(network))]

    return arcs_lbl, network


def max_network_distance(geoPts):
    if not isinstance(geoPts, dict):
        raise Exception('geoPts must be a type dict and in format {region:(lat,lng)}')

    dist = [geodesic(tuple([geoPts[f][0], geoPts[f][1]]), tuple(
        [geoPts[t][0], geoPts[t][1]])).miles for f, t in list(permutations(geoPts.keys(), 2))]

    return max(dist)


if __name__ == '__main__':

    gdxin = gt.gdxrw.gdxReader('./gdx_temp/nodes.gdx')

    i = gdxin.rgdx(name='i')
    lat = gdxin.rgdx(name='lat')
    lng = gdxin.rgdx(name='lng')
    map_aggr = gdxin.rgdx(name='map_aggr')

    agg = pd.DataFrame(index=i['elements'])
    agg['lat'] = pd.DataFrame(data=lat['values'].values(), index=lat['values'].keys())
    agg['lng'] = pd.DataFrame(data=lng['values'].values(), index=lng['values'].keys())

    agg_pts = dict(zip(agg.index, list(zip(agg.lat, agg.lng))))

    # create transmission network with Delaunay triangulation
    # triangulate WI FIPS regions as the core of the network

    ij_regions, grid = create_transmission_network(geoPts=agg_pts)

    # create gdx container
    gdxout = gt.gdxrw.gdxWriter('./gdx_temp/network_arcs.gdx')

    gdxout.add_set_dc(gamssetname='ij',
                      domain=['regions', 'regions'],
                      toset=ij_regions,
                      desc='transmission arcs in the model')

    gdxout.export_gdx()
