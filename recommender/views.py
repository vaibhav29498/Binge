from django.shortcuts import render
from urllib.request import urlopen
from recommender.models import Anime, Genre
import json
from sklearn import linear_model


def binary_search(ls, x):
    left = 0
    right = len(ls) - 1
    while left <= right:
        mid = (left + right) // 2
        if ls[mid] == x:
            return mid
        elif ls[mid] > x:
            right = mid - 1
        else:
            left = mid + 1
    return -1


def index(request):
    return render(request, 'recommender/index.html')


def credits(request):
    return render(request, 'recommender/credits.html')


def recommender(request):
    with urlopen('https://kuristina.herokuapp.com/anime/' + str(request.POST.get('username')) + '.json') as url:
        userdata = json.loads(url.read().decode())
    a = userdata['myanimelist']['anime']
    X = []
    y = []
    l = []
    for x in a:
        if x['my_score'] != '0':
            try:
                obj = Anime.objects.get(aid=int(x['series_animedb_id']))
            except obj.DoesNotExist:
                continue
            l.append(obj.aid)
            genre = [0] * 43
            for g in obj.genre.all():
                genre[g.gid - 1] = 1
            X.append([float(obj.rating), obj.members] + genre)
            y.append(float(x['my_score']))
        elif x['my_watched_episodes'] != '0':
            l.append(int(x['series_animedb_id']))

    if len(y) == 0:
        err = 'No recommendations can be generated since you haven\'t rated any anime.'
        return render(request, 'recommender/list.html', {'userid': request.POST['username'], 'error': err})

    clf = linear_model.ElasticNet(alpha=0.1)
    clf.fit(X, y)
    recommendations = []

    for x in Anime.objects.all():
        if x.aid in l or x.members < 100:
            continue
        genre = [0] * 43
        for g in x.genre.all():
            genre[g.gid - 1] = 1
        h = clf.predict([[x.rating, x.members] + genre])[0]
        recommendations.append([x.aid, x.name, h])

    recommendations = sorted(recommendations, key=lambda v: v[2], reverse=True)
    c = 0
    i = -1
    recc_id = []
    reccs = []
    while c < 50:
        i += 1
        obj = Anime.objects.get(aid=recommendations[i][0])
        if len(set(recc_id).intersection([x.aid for x in obj.related.all()])) >= 2:
            continue
        recc_id.append(recommendations[i][0])
        reccs.append(obj)
        c += 1

    return render(request, 'recommender/list.html', {'userid': request.POST['username'], 'recc': reccs})
