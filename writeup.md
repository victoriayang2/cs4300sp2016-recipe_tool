Each line in allrecipes.json is a json object like this
```json
{
    "code": "String",
    "tag": "String",
    "name": "String",
    "desc": "String",
    "time": "Int",
    "servings": "Int",
    "calories": "Int",
    "ing": "List(String)",
    "steps": "List(String)",
    "tips": "List(String)",
    "rating": "Float",
    "num_reviews": "Int",
    "reviews": [{
        "reviewer": "String",
        "rating": "Int",
        "text": "String"
    }],
}
```
Given a recipe url
```
http://allrecipes.com/recipe/13896/tofu-parmigiana/
```
and a url of a user who reviewed this recipe (!!not the review url!!)
```
http://allrecipes.com/cook/1091652/
```
we get the following
```python
recipe['code'] = '13896'
recipe['tag'] = 'tofu-parmigiana'
#and
review['reviewer'] = '1091652'
```
