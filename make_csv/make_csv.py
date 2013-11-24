# -*- coding: utf-8 -*-
import re, csv, os, json
import argparse
from warnings import catch_warnings

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
            for row in rd:
                hira = hiragana(row[12])
                sei = daku_to_sei(hira)
                sei_search = sei[-2:]
                try:
                    d = json.dumps({
                        'surface': row[0],
                        'reading': hira,
                        'reading_seion': sei,
                        'reading_search': sei_search,
                        'count_hira': len(hira),
                        'loc': [float(row[14]), float(row[15])]
                    },  ensure_ascii=False)
                    jsondump.append(d)
                except ValueError as e:
                    print("エラーのためスキップ:" + str(e))

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
