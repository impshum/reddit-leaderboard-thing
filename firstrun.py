from requests import get
import pickledb
import praw
import configparser


config = configparser.ConfigParser()
config.read('conf.ini')
client_id = config['REDDIT']['client_id']
client_secret = config['REDDIT']['client_secret']
reddit_user = config['REDDIT']['reddit_user']
reddit_pass = config['REDDIT']['reddit_pass']
target_subreddit = config['REDDIT']['target_subreddit']
target_submission = config['REDDIT']['target_submission']

db = pickledb.load('data.db', False)

reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     user_agent='Leaderboard thing (by /u/impshum)',
                     username=reddit_user,
                     password=reddit_pass)


def get_data():
    return get('https://www.bigbuckhd.com/world/qualifiers_search?order_by=SkillRank&order_direction=desc&limit=100&offset=0').json()


def main():
    for item in get_data():
        name = item['name'].strip()
        rank = str(item['overall_rank'])
        db.set(rank, name)
    db.dump()


if __name__ == '__main__':
    main()
