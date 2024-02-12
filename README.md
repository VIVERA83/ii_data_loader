# ii_data_loader
The service for uploading data from an excel file to the database of the "engineer instructor" application
-------


Монтировать образ
```bash
docker build -t data_loader .
```



Запуск приложения, Пример замените значения `token` и `client_id`
```bash
docker run --name data_loader -p 8006:8006 -e YA_TOKEN="token" -e YA_CLIENT_ID="client_id" data_loader
```

```bash
  docker build  -t data_loader .
```
```bash
  docker push vivera83/ii_data_loader:2
```
```bash
  docker build -t vivera83/ii_data_loader:2 .
```

https://yandex.ru/dev/disk/doc/ru/concepts/quickstart#quickstart__oauth