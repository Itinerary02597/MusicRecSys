# -*- coding:utf-8 -*-
from sing.models import SingTag
from song.models import SongTag
from user.models import UserBrowse
from playlist.models import PlayListToSongs, PlayListToTag

# 首页 推荐标签
"""
    由于标签个数原因，且歌单、歌手、歌曲公用一套标签，所以这里的标签推荐基于
        1、用户进入系统时的选择
        2、用户在站内产生的点击行为
        3、热门标签进行补数
"""

def GetRecTags(request, base_click):
    # 从接口中获取传入的歌手和歌曲id
    # sings = request.GET.get("sings").split(",")
    # songs = request.GET.get("songs").split(",")
    sings = request.session["sings"].split(",")
    songs = request.session["songs"].split(",")
    # 歌手标签
    sings_tags = getSingRecTags(sings, base_click)
    # 歌曲标签
    songs_tags,pl_tags = getSongAndPlRecTags(songs, base_click)
    return {
        "code": 1,
        "data": {
            "playlist": {"cateid": 2, "tags": list(pl_tags)},
            "song": {"cateid": 3, "tags": list(songs_tags)},
            "sing": {"cateid": 4, "tags": list(sings_tags)},
        }
    }


# 获得歌手标签推荐
def getSingRecTags(sings, base_click):
    sings_tags_by_click = set()
    sings_tags_by_choose = set()
    sings_tags_by_hot = set()
    # base_click =1 表示用户是在站内产生行为后返回为你推荐，此时用户行为对象对应的标签排序在前
    # 否则基于用户选择的标签排序在前
    if base_click == 1:
        click_sings = UserBrowse.objects.filter(click_cate="4").values("click_id")
        if click_sings.__len__() != 0:
            for one in click_sings:
                filter_one = SingTag.objects.filter(sing_id=one["click_id"])
                if filter_one.__len__() != 0:
                    sings_tags_by_click.add(filter_one[0].tag)
        # print("sings_tags_by_click: %s" % sings_tags_by_click)
    else:
        if sings.__len__() != 0:  # 表示前端选择了相关歌手
            for sing in sings:
                choose_one = SingTag.objects.filter(sing_id=sing)
                if choose_one.__len__() != 0:
                    sings_tags_by_choose.add(choose_one[0].tag)
            # print("sings_tags_by_choose: %s" % sings_tags_by_choose)
    # 如果 click 和 choose的tag不够 以 hot来补充
    if (sings_tags_by_click & sings_tags_by_choose).__len__() < 15:
        hot_tag_dict = dict()
        for one in SingTag.objects.all():
            hot_tag_dict.setdefault(one.tag, 0)
            hot_tag_dict[one.tag] += 1
        tag_dict_sing = sorted(hot_tag_dict.items(), key=lambda k: k[1], reverse=True)[:15]
        sings_tags_by_hot = set( [one[0] for one in tag_dict_sing] )
        # print("sings_tags_by_hot: %s" % sings_tags_by_hot)

    # 最终返回的歌手标签进行拼接
    last_sings_tags = list()
    if base_click == 1:  # 先 append click 得到的标签
        for tag in sings_tags_by_click:
            if tag not in last_sings_tags:
                last_sings_tags.append(tag)
        for tag in sings_tags_by_choose:
            if tag not in last_sings_tags:
                last_sings_tags.append(tag)
    else:  # 先 append choose 得到的标签
        for tag in sings_tags_by_choose:
            if tag not in last_sings_tags:
                last_sings_tags.append(tag)
        for tag in sings_tags_by_click:
            if tag not in last_sings_tags:
                last_sings_tags.append(tag)
    _need_len = 15 - last_sings_tags.__len__()
    for tag in list(sings_tags_by_hot)[:_need_len]:
        if tag not in last_sings_tags:
            last_sings_tags.append(tag)
    return list(last_sings_tags)


# 获得歌曲、歌单标签推荐
def getSongAndPlRecTags(songs, base_click):
    songs_tags_by_click = set()
    songs_tags_by_choose = set()
    songs_tags_by_hot = set()

    pl_tags_by_click = set()
    pl_tags_by_choose = set()
    pl_tags_by_hot = set()

    if base_click == 1: # 表示前端是基于点击行为进入为你推荐模块
        click_songs = UserBrowse.objects.filter(click_cate="3").values("click_id")
        if click_songs.__len__() != 0:
            for one in click_songs:
                filter_one = SongTag.objects.filter(song_id=one["click_id"])
                if filter_one.__len__() != 0:
                    songs_tags_by_click.add(filter_one[0].tag)

                    # 歌单tag
                    pl_one = PlayListToSongs.objects.filter( song_id=filter_one[0].song_id )
                    if pl_one.__len__() !=0:
                        for pl_tag_one in PlayListToTag.objects.filter(pl_id=pl_one[0].song_id):
                            pl_tags_by_click.add(pl_tag_one.tag)
        # print("songs_tags_by_click %s" % songs_tags_by_click)
        # print("pl_tags_by_click %s" % pl_tags_by_click)
    else:     # 表示用户是首次进入为你推荐模块
        if songs.__len__() != 0:  # 表示前端选择了相关歌曲
            for sing in songs:
                choose_one = SongTag.objects.filter(song_id=sing)
                if choose_one.__len__() != 0:
                    songs_tags_by_choose.add(choose_one[0].tag)

                    # 歌单tag
                    pl_one = PlayListToSongs.objects.filter(song_id=choose_one[0].song_id)
                    if pl_one.__len__() != 0:
                        for pl_tag_one in PlayListToTag.objects.filter(pl_id=pl_one[0].song_id):
                            pl_tags_by_choose.add(pl_tag_one.tag)
            # print("songs_tags_by_choose: %s" % songs_tags_by_choose)
            # print("pl_tags_by_choose: %s" % pl_tags_by_choose)
    # 如果 click 和 choose的tag不够 以 hot来补充
    if (songs_tags_by_click & songs_tags_by_choose).__len__() < 15:
        hot_tag_dict = dict()
        for one in SongTag.objects.all():
            hot_tag_dict.setdefault(one.tag, 0)
            hot_tag_dict[one.tag] += 1
        tag_dict_song = sorted(hot_tag_dict.items(), key=lambda k: k[1], reverse=True)[:15]
        for one in tag_dict_song:
            songs_tags_by_hot.add(one[0])
        # print("songs_tags_by_hot: %s" % songs_tags_by_hot)

    # 如果 click 和 choose的tag不够 以 hot来补充
    if (pl_tags_by_click & pl_tags_by_choose).__len__() < 15:
        hot_tag_dict = dict()
        for one in PlayListToTag.objects.all():
            hot_tag_dict.setdefault(one.tag, 0)
            hot_tag_dict[one.tag] += 1
        tag_dict_pl = sorted(hot_tag_dict.items(), key=lambda k: k[1], reverse=True)[:15]
        for one in tag_dict_pl:
            pl_tags_by_hot.add(one[0])
        # print("pl_tags_by_hot: %s" % pl_tags_by_hot)

    # 最终返回的歌曲标签进行拼接
    last_songs_tags = list()
    if base_click == 1:  # 先 append click 得到的标签
        for tag in songs_tags_by_click:
            if tag not in last_songs_tags:
                last_songs_tags.append(tag)
        for tag in songs_tags_by_choose:
            if tag not in last_songs_tags:
                last_songs_tags.append(tag)
    else:  # 先 append choose 得到的标签
        for tag in songs_tags_by_choose:
            if tag not in last_songs_tags:
                last_songs_tags.append(tag)
        for tag in songs_tags_by_click:
            if tag not in last_songs_tags:
                last_songs_tags.append(tag)
    _need_len = 15 - last_songs_tags.__len__()
    for tag in list(songs_tags_by_hot)[:_need_len]:
        if tag not in last_songs_tags:
            last_songs_tags.append(tag)

    # 最终返回的歌曲标签进行拼接
    last_pl_tags = list()
    if base_click == 1:  # 先 append click 得到的标签
        for tag in pl_tags_by_click:
            if tag not in last_pl_tags:
                last_pl_tags.append(tag)
        for tag in pl_tags_by_choose:
            if tag not in last_pl_tags:
                last_pl_tags.append(tag)
    else:  # 先 append choose 得到的标签
        for tag in pl_tags_by_choose:
            if tag not in last_pl_tags:
                last_pl_tags.append(tag)
        for tag in pl_tags_by_click:
            if tag not in last_pl_tags:
                last_pl_tags.append(tag)
    _need_len = 15 - last_pl_tags.__len__()
    for tag in list(pl_tags_by_hot)[:_need_len]:
        if tag not in last_pl_tags:
            last_pl_tags.append(tag)

    return list(last_songs_tags),list(last_pl_tags)
