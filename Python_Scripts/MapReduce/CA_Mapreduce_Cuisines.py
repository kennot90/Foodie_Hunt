from bson.code import Code
import pymongo

map = Code(
    """function () { \
        rest_id = this._id; \
        rest_rank = this.Rank; \
        this.Cuisine.split(",").forEach(function(cui) { \
            var key = cui.trim(); \
            if(key !== ""){ \
                var value = { \
                    total_count: 1, \
                    rest_id: rest_id, \
                    rank: rest_rank \
                }; \
                emit(key, value); \
            } \
        }); \
}"""
)

reduce = Code(
    """function (key, values) { \
        var total = 0; \
        var restaurants_array = []; \
        top_ranked_restaurants = []; \
        for (var i = 0; i < values.length; i++) { \
            total += values[i]['total_count']; \
            restaurants_array.push({ \
                name: values[i]['rest_id'], \
                value: values[i]['rank'] \
            }); \
        } \
        \
        restaurants_array.sort(function(a, b) { \
            return (a.value > b.value) ? -1 : ((b.value > a.value) ? 1 : 0); \
        }); \
        \
        for(var i = 0; i < restaurants_array.length; i++) { \
            var legal_name = restaurants_array[i]['name']; \
            if(typeof legal_name  !== 'undefined') { \
                top_ranked_restaurants.push(legal_name); \
            } \
            if(top_ranked_restaurants.length == 10){
                break;
            }
        }\
        var result = { \
            total_count: total, \
            restaurant_ids: top_ranked_restaurants \
        };\
        return result; \
    }"""
)

connection = pymongo.MongoClient("mongodb://localhost")
db = connection.FoodieHunt
restaurants = db.restaurants

db.restaurants.map_reduce(map, reduce, "cuisines")