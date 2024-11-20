###Запустите команду для сборки и запуска контейнера:
```
docker-compose up --build
```
Это соберёт исходники внутри docker контейнра и запустит тесты, вывод будет
направлен в консоль.


###Отладка(если необходимо)
```
docker run -it --rm --cap-add=SYS_ADMIN --device /dev/fuse --mount type=tmpfs,destination=/mnt/memfs_mount_point memfs-test /bin/bash
```
