# ii_data_loader
The service for uploading data from an excel file to the database of the "engineer instructor" application
-------


Монтировать образ
```bash
docker build -t my_app .
```
Запуск приложения, Пример замените значения `token` и `client_id`
```
docker run --name APP -p 8005:8005 -e YA_TOKEN="token" -e YA_CLIENT_ID="client_id" my_app
```
