from django.shortcuts import render
from urllib.request import urlopen
from recommender.models import Anime, Genre
import json
from sklearn import linear_model
import numpy as np


def index(request):
    return render(request, 'recommender/index.html')

def credits(request):
    return render(request, 'recommender/credits.html')


def recommender(request):
    try:
        with urlopen('https://myanimelist.net/animelist/' + str(request.POST.get('username')) + '/load.json?status=7&offset=0') as url:
            a = json.loads(url.read().decode())
    except:
        err = 'Invalid username!'
        return render(request, 'recommender/list.html', {'userid': request.POST['username'], 'error': err})
    X = []
    G = []
    y = []
    l = []
    feature_detail = []

    for i in range(43):
        feature_detail.append([i])

    for i in range(43):
        for j in range(i, 43):
            feature_detail.append([i, j])

    for x in a:
        if x['score'] != '0':
            try:
                obj = Anime.objects.get(aid=int(x['anime_id']))
            except obj.DoesNotExist:
                continue
            l.append(obj.aid)
            genre = [0] * 43
            for g in obj.genre.all():
                genre[g.gid - 1] = 1
            # gl = len(genre)
            # for i in range(gl):
            #     for j in range(i + 1, gl):
            #         genre.append(genre[i] * genre[j])
            G.append(genre)
            X.append([float(obj.rating), obj.members])# + genre)
            y.append(float(x['score']))
        elif x['num_watched_episodes'] != '0':
            l.append(int(x['anime_id']))

    if len(y) == 0:
        err = 'No recommendations can be generated since you haven\'t rated any anime.'
        return render(request, 'recommender/list.html', {'userid': request.POST['username'], 'error': err})

    X = np.array(X, dtype=float)
    G = np.array(G, dtype=float)
    y = np.array(y, dtype=float)

    clf = linear_model.ElasticNet(alpha=0.2)
    clf2 = linear_model.LinearRegression()
    clf.fit(G, y)
    coeff = [idx for idx, x in enumerate(clf.coef_) if x != 0]
    # print(coeff, np.hstack((X, G[:, coeff]))[0])
    clf2.fit(np.hstack((X, G[:, coeff])), y)

    recommendations = []
    for x in Anime.objects.all():
        if x.aid in l or x.members < 100:
            continue
        genre = [0] * 43
        for g in x.genre.all():
            genre[g.gid - 1] = 1
        gl = []
        for i in coeff:
            j = 1
            for k in feature_detail[i]:
                j *= genre[k]
            gl.append(j)
        h = clf2.predict([[x.rating, x.members] + gl])[0]
        recommendations.append([x.aid, x.name, h])

    recommendations = sorted(recommendations, key=lambda v: v[2], reverse=True)
    c = 0
    i = -1
    recc_id = []
    reccs = []
    while c < 50:
        i += 1
        obj = Anime.objects.get(aid=recommendations[i][0])
        if len(set(recc_id).intersection([x.aid for x in obj.related.all()])) >= 1:
            print(obj.name)
            continue
        recc_id.append(recommendations[i][0])
        reccs.append(obj)
        c += 1
    # print(recommendations[0], clf2.coef_)
    # l = clf.coef_
    # for i in range(1, 44):
    #     print(Genre.objects.get(gid=i).name, l[i - 1])
    # x = 43
    # for i in range(1, 44):
    #     print(Genre.objects.get(gid=i).name, end=': ')
    #     for j in range(i, 43):
    #         print(Genre.objects.get(gid=j).name + ' ', l[x], end=' ')
    #         x += 1
    #     print('')
    return render(request, 'recommender/list.html', {'userid': request.POST['username'], 'recc': reccs})
