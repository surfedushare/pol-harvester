# SURFnet Rating application

## Project setup

```
npm install
```

### Compiles and hot-reloads for development
```
npm run serve
```

### Compiles and minifies for production
```
npm run build
```


## Selecting a freeze

A default Freeze can be set in the .env file by setting the value of **VUE_APP_DEFAULT_FREEZE** to the Freeze name. 

The default Freeze can be overwritten by using the following query in the URL:
```
http://localhost:8080?freeze=<freeze_name>
```

## Elastic Search Query

All calls to the ElasticSearch environment can be found in the **elasticSearchService** (*elasticsearch.service.js*) in the *_services* folder. 
To change the query that's being performed, change the **query** object in the **get()** function.
