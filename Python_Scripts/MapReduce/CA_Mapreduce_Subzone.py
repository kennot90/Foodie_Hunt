from bson.code import Code
import pymongo

map = Code(
    """function () { \
        rest_id = this._id; \
        key = this.Subzone.trim(); \
        cuisine = this.Cuisine; \
        if(key !== ""){ \
            cuisine.split(",").forEach(function(cui) { \
                var value = { \
                    rest_cuisine: cui.trim(), \
                    total_count: 1 \
                }; \
                emit(key, value); \
            }); \
        } \
    }"""
)

reduce = Code(
    """function (key, values) { \
        var total = 0; \
        var cuimap = {}; \
        for (var i = 0; i < values.length; i++) { \
            var value_dict = values[i]; \
            if(typeof value_dict  !== 'undefined' && typeof value_dict['rest_cuisine'] !== 'undefined') { \
                total += value_dict['total_count']; \
                 if(value_dict['rest_cuisine'] in cuimap) {  \
                    cuimap[value_dict['rest_cuisine']] += value_dict['total_count']; \
                 } \
                 else { \
                   cuimap[value_dict['rest_cuisine']] = value_dict['total_count']; \
                 } \
            } \
        } \
        var result = { \
            total_count: total, \
            cuisine: cuimap \
        };\
        return result; \
    }"""
)

connection = pymongo.MongoClient("mongodb://localhost")
db = connection.FoodieHunt
restaurants = db.restaurants

db.restaurants.map_reduce(map, reduce, "subzone")