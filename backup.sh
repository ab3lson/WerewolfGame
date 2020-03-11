DBNAME=werewolf
DATE=$(date +"%FT%T")
SQLFILE=$DBNAME-${DATE}.sql
mysqldump --opt --user=tyler --password=$PASSWORD $DBNAME > $SQLFILE
gzip $SQLFILE
mv --force $SQLFILE.gz /home/tyler/.

