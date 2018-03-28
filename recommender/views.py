from django.shortcuts import render
from urllib.request import urlopen
from recommender.models import Anime, Genre
import json


def index(request):
    return render(request, 'recommender/index.html')


def credits(request):
    return render(request, 'recommender/credits.html')

def recommender(request):
    with urlopen('https://kuristina.herokuapp.com/anime/' + str(request.POST.get('username')) + '.json') as url:
        userdata = json.loads(url.read().decode())
    a = userdata['myanimelist']['anime']
    anime = []
    l = []
    for x in a:
        if x['my_score'] != '0':
            anime.append([Anime.objects.get(aid=int(x['series_animedb_id'])), int(x['my_score'])])
            l.append(int(x['series_animedb_id']))
    for a in anime:
        a.append([g.gid for g in a[0].genre.all()])

    recommendations = []

    # Parameters
    relf = 2
    maxrel = 1
    userscore_weight = 1.25
    popular_max = 2
    popular_mid = 50000

    for x in Anime.objects.all():
        y = 0
        g = set([v.gid for v in x.genre.all()])
        r = [v.aid for v in x.related.all()]
        for z in anime:
            sim = len(g.intersection(z[2])) / len(g.union(z[2]))
            y += ((float(x.rating) * z[1]) / (userscore_weight * float(x.rating) + z[1])) * sim * (relf if z[0].aid in r else 1)
        y *= (popular_max - (popular_mid / (popular_mid + x.members)))
        recommendations.append([x, y, r])

    recommendations = sorted(recommendations, key=lambda v: v[1], reverse=True)
    c = 0
    i = -1
    recc_id = []
    reccs = []
    while c < 100:
        i += 1
        if recommendations[i][0].aid in l or len(set(recc_id).intersection(recommendations[i][2])) >= maxrel:
            continue
        recc_id.append(recommendations[i][0].aid)
        reccs.append(recommendations[i][0])
        c += 1

    return render(request, 'recommender/list.html', {'userid': request.POST['username'], 'recc': reccs})
