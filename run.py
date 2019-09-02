from requests import get
import pickledb
import praw
import schedule
from time import sleep
from datetime import datetime
import configparser


config = configparser.ConfigParser()
config.read('conf.ini')
client_id = config['REDDIT']['client_id']
client_secret = config['REDDIT']['client_secret']
reddit_user = config['REDDIT']['reddit_user']
reddit_pass = config['REDDIT']['reddit_pass']
target_subreddit = config['REDDIT']['target_subreddit']
target_submission = config['REDDIT']['target_submission']
schedule_hours = config['REDDIT']['schedule_hours']

db = pickledb.load('data.db', False)

reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     user_agent='Leaderboard thing (by /u/impshum)',
                     username=reddit_user,
                     password=reddit_pass)


def get_data():
    return get('https://www.bigbuckhd.com/world/qualifiers_search?order_by=SkillRank&order_direction=desc&limit=100&offset=0').json()


def first_run():
    for item in get_data():
        name = item['name'].strip()
        rank = str(item['overall_rank'])
        db.set(rank, name)
    db.dump()


def get_new_data():
    data = get_data()
    new_data = {}
    for item in data:
        name = item['name'].strip()
        rank = str(item['overall_rank'])
        new_data.update({name: rank})
    return new_data


def post_text(target_subreddit, post_text):
    reddit.submission(id=target_submission).edit(post_text)


def go():
    new_data = get_new_data()
    now = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    table = 'Rank|Name|Change\n:-:|:-:|:-:\n'
    for x in db.getall():
        name = db.get(x)
        old_rank = new_data[db.get(x)]
        new_rank = x
        change = int(old_rank) - int(new_rank)
        line = f'**{new_rank}**|{name}|{change}\n'
        table += line
    post_text(target_subreddit, table)
    print(f'Updated {now}')


def main():
    go()
    schedule.every(int(schedule_hours)).hours.do(go)
    while True:
        schedule.run_pending()
        sleep(1)


if __name__ == '__main__':
    first_run()
    main()
