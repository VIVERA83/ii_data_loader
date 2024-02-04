# ii_data_loader
The service for uploading data from an excel file to the database of the "engineer instructor" application
-------


Монтировать образ
```bash
docker build -t ii_data_loader .
```
Запуск приложения, Пример замените значения `token` и `client_id`
```
docker run --name data_loader -p 8006:8006 -e YA_TOKEN="token" -e YA_CLIENT_ID="client_id" ii_data_loader
```

```bash
  docker build  -t data_loader .
```