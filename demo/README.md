This is a simple demo REST API app with a single endpoint.


Install the requirements via
```bash
pip install -r requirements.txt
```
You also need a MongoDB instance running in the background on `localhost:27017` for it to work.

Run the app via
```bash
python3 app.py
```

Now you should be able to visit it on `localhost:8000`.

#### The API

The only endpoint of the app is `/todos/`.

Make a `POST` request in order to create a new todo item with a paylaod like this:
```json
{
    "title": "Very important task",
    "description": "Gotta go make some money, you know"
}
```

Make a few of these to populate the DB and then run `GET` requests with 
different filters, sorting and pagination options.

Example queries:
- Sort by title [http://localhost:8000/todos/?sort=title](http://localhost:8000/todos/?sort=title)
- Sort by title descending [http://localhost:8000/todos/?sort=-title](http://localhost:8000/todos/?sort=-title)
- Skip 2 items and limit the output only 3 items [http://localhost:8000/todos/?skip=2&limit=3](http://localhost:8000/todos/?skip=2&limit=3)
- Sort by creation time [http://localhost:8000/todos/?sort=creation-time](http://localhost:8000/todos/?sort=creation-time)
- Sort by creation time (newest first) [http://localhost:8000/todos/?sort=-creation-time](http://localhost:8000/todos/?sort=-creation-time)
- Find items with a certain title [http://localhost:8000/todos/?title=foo](http://localhost:8000/todos/?title=foo)
- Find items created after certain time [http://localhost:8000/todos/?time[min]=2022-05-15T16:17:47.08518](http://localhost:8000/todos/?time[min]=2022-05-15T16:17:47.085188)






