# -*- coding: utf-8 -*-
import re, csv, os
import argparse

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

    # 変換元のCSVの1行目(表示)、13行目(フリガナ)をもとに
    # 表示・ふりがな・清音ふりがな、文字数という形に変換する
    with open(args.file_path, newline='', encoding='euc_jp') as rfile:
        with open(file_name + '_out.csv', 'w', encoding='utf-8', newline='') as wfile:
            rd = csv.reader(rfile)
            writer = csv.writer(wfile, lineterminator='\n')
            # ヘッダの追加
            writer.writerow(['surface', 'reading', 'reading_seion', 'count_hira'])
            for row in rd:
                hira = hiragana(row[12])
                writer.writerow([row[0], hira, daku_to_sei(hira), len(hira)])
