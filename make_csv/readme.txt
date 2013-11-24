mongo db import コマンド
mongoimport -h <host> --port <port> -u <urser> -p <pass> -d <dbs> -c words --type csv --file <filepath> --headerline

mongoimport -h <host> --port <port> -u <urser> -p <pass> -d <dbs> -c words --type json --file <filepath>

INDEX:
db.words.ensureIndex( { "reading_search" : 1} )
db.words.ensureIndex( { "loc": "2d" } )