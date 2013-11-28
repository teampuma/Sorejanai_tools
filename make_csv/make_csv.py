# -*- coding: utf-8 -*-
import re, csv, os, json, time
import argparse
from geopy.geocoders import GoogleV3
from geopy.exc import GeocoderQuotaExceeded

'''
めかぶの名詞ファイルから
SorejanaiのWordに格納できるCSVに変換するスクリプト
作成したCSVファイルはmongo import すること

たぶんPython3のみの対応
'''


def hiragana(text):
    # カタカナをひらがなに変換するメソッド
    re_kata = re.compile('[ァ-ヴ]')
    return re_kata.sub(lambda x: chr(ord(x.group(0)) - 0x60), text)


def daku_to_sei(s):
    # 濁点ありのひらがなをなしに変換するメソッド
    dakuon = 'がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽ'
    seion = 'かきくけこさしすぜそたちつてとはひふへほはひふへほ'

    ret = s
    for i in range(len(dakuon)):
        ret = ret.replace(dakuon[i], seion[i])
    return ret


if __name__ == '__main__':
    # FILE名を受け取って、ひらがな・清音ひらがな・文字数を追加する
    parser = argparse.ArgumentParser('mecab csv -> Sorejanai csv')
    # 変換対象のファイルパス
    parser.add_argument('file_path')
    args = parser.parse_args()
    file_full_name = os.path.basename(args.file_path)
    file_name = '.'.join(file_full_name.split(sep='.')[:-1])

    geolocator = GoogleV3()
    # 最初に場所ファイルかチェック
    # 場所や座標があったら場所ファイルと判断
    locfile = False
    with open(args.file_path, newline='', encoding='euc_jp') as f:
        rd = csv.reader(f)
        for row in rd:
            if len(row) > 13:
                locfile = True

    if locfile:
        # 場所ファイルの場合はjsonに変換。座標情報がうまく入らないので
        jsondump = []
        with open(args.file_path, encoding='euc_jp') as rfile:
            rd = csv.reader(rfile)
            exceed = False
            cnt_00 = cnt_chg = cnt_not = 0
            for row in rd:
                hira = hiragana(row[12])
                sei = daku_to_sei(hira)
                sei_search = sei[-2:]

                lon = lat = 0.0
                try:
                    lon, lat = float(row[14]), float(row[15])
                except ValueError as e:
                    print("エラーのためスキップ:" + str(e))
                    continue

                # 経度と緯度の取得
                if lon == 0.0 and lat == 0.0:
                    cnt_00 += 1
                    if not exceed:
                        cnt_chg += 1
                        # ０，０の場合は場所が取れてなかったもの。適当な値を入れる
                        try:
                            tmp = geolocator.geocode(row[0])
                            time.sleep(1)
                            if tmp:
                                # ヒットしたらセット。しなかったらスルー
                                _, (lat, lon) = tmp
                            else:
                                cnt_not += 1
                        except GeocoderQuotaExceeded:
                            exceed = True

                d = json.dumps({
                    'surface': row[0],
                    'reading': hira,
                    'reading_seion': sei,
                    'reading_search': sei_search,
                    'count_hira': len(hira),
                    'loc': [lon, lat]
                },  ensure_ascii=False)
                jsondump.append(d)
            print("緯度経度変更対象：%d件　変更済み：%d件　変更できなかった：%d件" % (cnt_00, cnt_chg, cnt_not))
        with open(file_name + '_out.json', 'w', encoding='utf-8') as wfile:
            for r in jsondump:
                wfile.write(r + '\n')

    else:
        # 変換元のCSVの1行目(表示)、13行目(フリガナ)をもとに
        # 表示・ふりがな・清音ふりがな、検索用ふりがな、文字数という形に変換する
        with open(args.file_path, newline='', encoding='euc_jp') as rfile:
            with open(file_name + '_out.csv', 'w', encoding='utf-8', newline='') as wfile:
                rd = csv.reader(rfile)
                writer = csv.writer(wfile, lineterminator='\n')
                # ヘッダの追加
                writer.writerow(['surface', 'reading', 'reading_seion', 'reading_search', 'count_hira'])
                for row in rd:
                    hira = hiragana(row[12])
                    sei = daku_to_sei(hira)
                    sei_search = sei[-2:]
                    writer.writerow([row[0], hira, sei, sei_search, len(hira)])
