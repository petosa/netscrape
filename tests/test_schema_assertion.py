import pytest

from netscrape.db_interface import db_interface

def test_simple_true():
    A = 3
    B = 4
    assert (db_interface.schema_assertion(None, A, B))
    A = "same"
    B = "type"
    assert (db_interface.schema_assertion(None, A, B))
    A = ""
    B = "type"
    assert (db_interface.schema_assertion(None, A, B))

def test_simple_false():
    A = 3
    B = "no"
    assert (not db_interface.schema_assertion(None, A, B))
    A = "2.4"
    B = 2.4
    assert (not db_interface.schema_assertion(None, A, B))
    A = 4
    B = 2.2
    assert (not db_interface.schema_assertion(None, A, B))

def test_simple_mixed_false():
    A = 3
    B = ["what"]
    assert(not db_interface.schema_assertion(None, A, B))
    A = "2.4"
    B = ["2.4"]
    assert (not db_interface.schema_assertion(None, A, B))
    A = {"key": 1}
    B = "key"
    assert (not db_interface.schema_assertion(None, A, B))
    A = {"key": 1}
    B = ["key"]
    assert (not db_interface.schema_assertion(None, A, B))
    A = {}
    B = []
    assert (not db_interface.schema_assertion(None, A, B))

def test_simple_collection_true():
    A = []
    B = []
    assert (db_interface.schema_assertion(None, A, B))
    A = {}
    B = {}
    assert (db_interface.schema_assertion(None, A, B))
    A = []
    B = [1, 2, 3, 4, "5"]
    assert (db_interface.schema_assertion(None, A, B))
    A = []
    B = []
    assert (db_interface.schema_assertion(None, A, B))

def test_medium_list_true():
    A = [1, 2, 3]
    B = [4, 5, 6, 7, 8, 9, 10]
    assert (db_interface.schema_assertion(None, A, B))
    A = [{}, {}, {}]
    B = [{}, {}, {}, {}, {}, {}, {}]
    assert (db_interface.schema_assertion(None, A, B))
    A = ["hi", "hi"]
    B = ["cool"]
    assert (db_interface.schema_assertion(None, A, B))
    A = [2.2, 3.2]
    B = [5.6, 6.3, 7.2, 8.7, 9.4, 10.6]
    assert (db_interface.schema_assertion(None, A, B))

def test_medium_list_false():
    A = [1, 2, 3]
    B = [4.1, 5, 6, 7, 8, 9, 10]
    assert (not db_interface.schema_assertion(None, A, B))
    A = ["", 2.2, 3]
    B = [4, 5, 6, 7.2, 8, 9, 10]
    assert (not db_interface.schema_assertion(None, A, B))
    A = ["hi", 2.2, 3]
    B = [{}, 5, 6, 7.2, 8, 9, 10]
    assert (not db_interface.schema_assertion(None, A, B))

def test_medium_dict_true():
    A = {"hey": 1234155135135135135153135135135135332523523531}
    B = {"hey": 1}
    assert (db_interface.schema_assertion(None, A, B))
    A = {"": ""}
    B = {"": "nematodes"}
    assert (db_interface.schema_assertion(None, A, B))
    A = {"a": "", "b": 2, "c": 15.1, "d": []}
    B = {"a": "hgwr", "b": 5, "c": 0.1, "d": []}
    assert (db_interface.schema_assertion(None, A, B))
    A = {"a": 1, "a": 2}
    B = {"a": "a", "a": 2}
    assert (db_interface.schema_assertion(None, A, B))

def test_medium_dict_false():
    A = {}
    B = {"hey": 1}
    assert (not db_interface.schema_assertion(None, A, B))
    A = {"hey":1, "why":2}
    B = {"hey":1}
    assert (not db_interface.schema_assertion(None, A, B))
    A = {"you":[], "are":2.1}
    B = {"you":"", "are":2}
    assert (not db_interface.schema_assertion(None, A, B))
    A = {"you": [], "are": 2}
    B = {"you": [], "are": 2.2}
    assert (not db_interface.schema_assertion(None, A, B))

def test_hard_true():
    A = {"hey": [[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]}
    B = {"hey": [[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]}
    assert (db_interface.schema_assertion(None, A, B))
    A = {"a":1, "b":[{"you": ["1"], "are": 2},{"you": ["geaeg"], "are": 624646}]}
    B = {"a": 4, "b": [{"you": ["5"], "are": 5},{"you": ["hrws"], "are": 2444}]}
    assert (db_interface.schema_assertion(None, A, B))
    A = {
       "_id": 2,
       "address": {
          "building": "1166",
          "coord": [ -73.955184, 40.738589 ],
          "street": "Manhattan Ave",
          "zipcode": "11222"
       },
       "borough": "Brooklyn",
       "cuisine": "Bakery",
       "grades": [
          { "date": { "$date": 1393804800000 }, "grade": "C", "score": 2.1 },
          { "date": { "$date": 1378857600000 }, "grade": "B", "score": 6.1 },
          { "date": { "$date": 1358985600000 }, "grade": "F", "score": 3.1 },
          { "date": { "$date": 1322006400000 }, "grade": "B", "score": 5.1 }
       ],
       "name": "Dainty Daisey's Donuts",
       "restaurant_id": "30075449"
    }
    B = {
       "_id": 5,
       "address": {
          "building": "eleven",
          "coord": [ -175.1, 41.59 ],
          "street": "Manhattan Ave",
          "zipcode": "n/a"
       },
       "borough": "Manhattan",
       "cuisine": "Chinese",
       "grades": [
          { "date": { "$date": 246246 }, "grade": "Cow", "score": 261.1 },
          { "date": { "$date": 24247247 }, "grade": "R", "score": 36.1 },
          { "date": { "$date": 135892472485600000 }, "grade": "U", "score": 663.1 },
          { "date": { "$date": 1322004277426400000 }, "grade": "N", "score": 15.1 }
       ],
       "name": "Gold Temple",
       "restaurant_id": "2744724"
    }
    assert (db_interface.schema_assertion(None, A, B))

def test_hard_false():
    A = {"hey": [[[[[[[[[[[1,[[[[[[[[[[[[[[[[[[[[[[[[[[[[[]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]}
    B = {"hey": [[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[]]],1]]],1]],1]]],1]]],1]],1]]]],1],1]]],1],1],1],1]]]]]]]]]]],1]]}
    assert (not db_interface.schema_assertion(None, A, B))
    A = {"a":1, "b":[{"you": ["1"], "are": 2},{},{}]}
    B = {"a": 4, "b": [{"you": [5], "are": 5}, {}, {}]}
    assert (not db_interface.schema_assertion(None, A, B))
    A = {
       "_id": 2,
       "address": {
          "building": "1166",
          "coord": [ -73.955184, 40.738589 ],
          "street": "Manhattan Ave",
          "zipcode": "11222"
       },
       "borough": "Brooklyn",
       "cuisine": "Bakery",
       "grades": [
          { "date": { "$date": 1393804800000 }, "grade": "C", "score": 2.1 },
          { "date": { "$date": 1378857600000 }, "grade": "B", "score": 6.1 },
          { "date": { "$date": 1358985600000 }, "grade": "F", "score": 3.1 },
          { "date": { "$date": 1322006400000 }, "grade": "B", "score": 5.1 }
       ],
       "name": "Dainty Daisey's Donuts",
       "restaurant_id": "30075449"
    }
    B = {
       "_id": 5,
       "address": {
          "building": "eleven",
          "coord": [ -175.1, 41.59 ],
          "street": "Manhattan Ave",
          "zipcode": "n/a"
       },
       "borough": "Manhattan",
       "cuisine": "Chinese",
       "grades": [
          { "date": { "$date": 246246 }, "grade": "Cow", "score": 261.1 },
          { "date": { "$date": 24247247 }, "grade": "R", "score": 36.1 },
          { "date": { "$date": 135892472485600000 }, "grade": "U", "score": 663.1 },
          { "date": { "$date": 1322004277426400000 }, "grade": "N", "score": 15.1 }
       ],
       "name": "Gold Temple",
       "restaurant_id": [4]
    }
    assert (not db_interface.schema_assertion(None, A, B))

def test_typecheck_lists_true():
    A = [[], [], [], []]
    B = [[], [], [3], []]
    assert (db_interface.schema_assertion(None, A, B))
    A = [[], [], [], [1]]
    B = [[], [], [3], []]
    assert (db_interface.schema_assertion(None, A, B))
    A = [[], [{"test":["hi"]}], [], [{"test":["hello"]}]]
    B = [[], [], [], [], []]
    assert (db_interface.schema_assertion(None, A, B))
    A = [[], [1], [], [2]]
    B = []
    assert (db_interface.schema_assertion(None, A, B))

def test_typecheck_lists_false():
    A = [1, 2, 3.3, 4]
    B = [1, 2, 3.3, 4]
    assert (not db_interface.schema_assertion(None, A, B))
    A = [1, 2, 3, 4]
    B = [1, 2, 3.3, 4]
    assert (not db_interface.schema_assertion(None, A, B))
    A = [[], [2.2], [], []]
    B = [[], [], [3], []]
    assert (not db_interface.schema_assertion(None, A, B))
    A = [[], [], [], [[1]]]
    B = [[], [], [3], []]
    assert (not db_interface.schema_assertion(None, A, B))
    A = [[], [2.2], [], [2]]
    B = [[], [], [], [], []]
    assert (not db_interface.schema_assertion(None, A, B))
    A = [[], [1], [], [2.2]]
    B = []
    assert (not db_interface.schema_assertion(None, A, B))

def test_real_world():
    A={"contributors": None, "truncated": False, "text": "\"Hans Blix: Whether Obama in #Syria or Bush in #Iraq, The US Is Not the World Police\" http://t.co/FQU4QMIxPF #propaganda #MiddleEast #war", "in_reply_to_status_id": None, "random_number": 0.29391851181222817, "id": 373208832580648960, "favorite_count": 0, "source": "<a href=\"http://twitter.com/tweetbutton\" rel=\"nofollow\">Tweet Button</a>", "retweeted": False, "coordinates": None, "entities": {"symbols": [], "user_mentions": [], "hashtags": [{"indices": [29, 35], "text": "Syria"}, {"indices": [47, 52], "text": "Iraq"}, {"indices": [109, 120], "text": "propaganda"}, {"indices": [121, 132], "text": "MiddleEast"}, {"indices": [133, 137], "text": "war"}], "urls": [{"url": "http://t.co/FQU4QMIxPF", "indices": [86, 108], "expanded_url": "http://huff.to/1dinit0", "display_url": "huff.to/1dinit0"}]}, "in_reply_to_screen_name": None, "id_str": "373208832580648960", "retweet_count": 0, "in_reply_to_user_id": None, "favorited": False, "user": {"follow_request_sent": None, "profile_use_background_image": True, "geo_enabled": False, "verified": False, "profile_image_url_https": "https://si0.twimg.com/profile_images/3537112264/5ebce8651eb68383030dc01836215da1_normal.jpeg", "profile_sidebar_fill_color": "FFF7CC", "id": 1360644582, "profile_text_color": "0C3E53", "followers_count": 27, "profile_sidebar_border_color": "F2E195", "location": "Detroit \u2663 Toronto", "default_profile_image": False, "id_str": "1360644582", "utc_offset": -14400, "statuses_count": 1094, "description": "Exorcising the sins of personal ignorance and accepted lies through reductionist analysis. Politics, economics, and science posts can be found here.", "friends_count": 81, "profile_link_color": "FF0000", "profile_image_url": "http://a0.twimg.com/profile_images/3537112264/5ebce8651eb68383030dc01836215da1_normal.jpeg", "notifications": None, "profile_background_image_url_https": "https://si0.twimg.com/images/themes/theme12/bg.gif", "profile_background_color": "BADFCD", "profile_banner_url": "https://pbs.twimg.com/profile_banners/1360644582/1366247104", "profile_background_image_url": "http://a0.twimg.com/images/themes/theme12/bg.gif", "name": "Neil Cheddie", "lang": "en", "following": None, "profile_background_tile": False, "favourites_count": 4, "screen_name": "Centurion480", "url": None, "created_at": "Thu Apr 18 00:34:18 +0000 2013", "contributors_enabled": False, "time_zone": "Eastern Time (US & Canada)", "protected": False, "default_profile": False, "is_translator": False, "listed_count": 2}, "geo": None, "in_reply_to_user_id_str": None, "possibly_sensitive": False, "lang": "en", "created_at": "Thu Aug 29 22:21:34 +0000 2013", "filter_level": "medium", "in_reply_to_status_id_str": None, "place": None, "_id": {"$oid": "521fc96edbef20c5d84b2dd8"}}
    B={"contributors": None, "truncated": False, "text": "\"Hans Blix: Whether Obama in #Syria or Bush in #Iraq, The US Is Not the World Police\" http://t.co/FQU4QMIxPF #propaganda #MiddleEast #war", "in_reply_to_status_id": None, "random_number": 0.29391851181222817, "id": 373208832580648960, "favorite_count": 0, "source": "<a href=\"http://twitter.com/tweetbutton\" rel=\"nofollow\">Tweet Button</a>", "retweeted": False, "coordinates": None, "entities": {"symbols": [], "user_mentions": [], "hashtags": [{"indices": [29, 35], "text": "Syria"}, {"indices": [47, 52], "text": "Iraq"}, {"indices": [109, 120], "text": "propaganda"}, {"indices": [121, 132], "text": "MiddleEast"}, {"indices": [133, 137], "text": "war"}], "urls": [{"url": "http://t.co/FQU4QMIxPF", "indices": [86, 108], "expanded_url": "http://huff.to/1dinit0", "display_url": "huff.to/1dinit0"}]}, "in_reply_to_screen_name": None, "id_str": "373208832580648960", "retweet_count": 0, "in_reply_to_user_id": None, "favorited": False, "user": {"follow_request_sent": None, "profile_use_background_image": True, "geo_enabled": False, "verified": False, "profile_image_url_https": "https://si0.twimg.com/profile_images/3537112264/5ebce8651eb68383030dc01836215da1_normal.jpeg", "profile_sidebar_fill_color": "FFF7CC", "id": 1360644582, "profile_text_color": "0C3E53", "followers_count": 27, "profile_sidebar_border_color": "F2E195", "location": "Detroit \u2663 Toronto", "default_profile_image": False, "id_str": "1360644582", "utc_offset": -14400, "statuses_count": 1094, "description": "Exorcising the sins of personal ignorance and accepted lies through reductionist analysis. Politics, economics, and science posts can be found here.", "friends_count": 81, "profile_link_color": "FF0000", "profile_image_url": "http://a0.twimg.com/profile_images/3537112264/5ebce8651eb68383030dc01836215da1_normal.jpeg", "notifications": None, "profile_background_image_url_https": "https://si0.twimg.com/images/themes/theme12/bg.gif", "profile_background_color": "BADFCD", "profile_banner_url": "https://pbs.twimg.com/profile_banners/1360644582/1366247104", "profile_background_image_url": "http://a0.twimg.com/images/themes/theme12/bg.gif", "name": "Neil Cheddie", "lang": "en", "following": None, "profile_background_tile": False, "favourites_count": 4, "screen_name": "Centurion480", "url": None, "created_at": "Thu Apr 18 00:34:18 +0000 2013", "contributors_enabled": False, "time_zone": "Eastern Time (US & Canada)", "protected": False, "default_profile": False, "is_translator": False, "listed_count": 2}, "geo": None, "in_reply_to_user_id_str": None, "possibly_sensitive": False, "lang": "en", "created_at": "Thu Aug 29 22:21:34 +0000 2013", "filter_level": "medium", "in_reply_to_status_id_str": None, "place": None, "_id": {"$oid": "521fc96edbef20c5d84b2dd8"}}
    assert (db_interface.schema_assertion(None, A, B))

if __name__ == '__main__':
    pytest.main()