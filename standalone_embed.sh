#!/usr/bin/env bash

# Licensed to the LF AI & Data foundation under one
# or more contributor license agreements. See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership. The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# 使用官方镜像
MILVUS_IMAGE="milvusdb/milvus:latest"

run_embed() {
    cat << EOF > embedEtcd.yaml
listen-client-urls: http://0.0.0.0:2379
advertise-client-urls: http://0.0.0.0:2379
quota-backend-bytes: 4294967296
auto-compaction-mode: revision
auto-compaction-retention: '1000'
EOF

    cat << EOF > user.yaml
# Extra config to override default milvus.yaml
EOF
    if [ ! -f "./embedEtcd.yaml" ]
    then
        echo "embedEtcd.yaml file does not exist. Please try to create it in the current directory."
        exit 1
    fi

    if [ ! -f "./user.yaml" ]
    then
        echo "user.yaml file does not exist. Please try to create it in the current directory."
        exit 1
    fi

    docker run -d \
        --name milvus-standalone \
        --security-opt seccomp:unconfined \
        -e ETCD_USE_EMBED=true \
        -e ETCD_DATA_DIR=/var/lib/milvus/etcd \
        -e ETCD_CONFIG_PATH=/milvus/configs/embedEtcd.yaml \
        -e COMMON_STORAGETYPE=local \
        -e DEPLOY_MODE=STANDALONE \
        -v $(pwd)/volumes/milvus:/var/lib/milvus \
        -v $(pwd)/embedEtcd.yaml:/milvus/configs/embedEtcd.yaml \
        -v $(pwd)/user.yaml:/milvus/configs/user.yaml \
        -p 19530:19530 \
        -p 9091:9091 \
        -p 2379:2379 \
        --health-cmd="curl -f http://localhost:9091/healthz" \
        --health-interval=30s \
        --health-start-period=90s \
        --health-timeout=20s \
        --health-retries=3 \
        $MILVUS_IMAGE \
        milvus run standalone  1> /dev/null
}

wait_for_milvus_running() {
    echo "⏳ 等待 Milvus 启动..."
    while true
    do
        res=`docker ps|grep milvus-standalone|grep healthy|wc -l`
        if [ $res -eq 1 ]
        then
            echo "✅ Milvus 启动成功！"
            break
        fi
        sleep 2
    done
}

start() {
    res=`docker ps|grep milvus-standalone|grep healthy|wc -l`
    if [ $res -eq 1 ]
    then
        echo "Milvus 已经在运行中。"
        exit 0
    fi

    res=`docker ps -a|grep milvus-standalone|wc -l`
    if [ $res -eq 1 ]
    then
        echo "🔄 启动已存在的 Milvus 容器..."
        docker start milvus-standalone 1> /dev/null
    else
        echo "📥 拉取镜像并启动 Milvus..."
        run_embed
    fi

    if [ $? -ne 0 ]
    then
        echo "❌ 启动失败。"
        exit 1
    fi

    wait_for_milvus_running
}

stop() {
    echo "⏹️  停止 Milvus..."
    docker stop milvus-standalone 1> /dev/null

    if [ $? -ne 0 ]
    then
        echo "❌ 停止失败。"
        exit 1
    fi
    echo "✅ Milvus 已停止。"

}

delete_container() {
    res=`docker ps|grep milvus-standalone|wc -l`
    if [ $res -eq 1 ]
    then
        echo "请先停止 Milvus 服务再删除。"
        exit 1
    fi
    docker rm milvus-standalone 1> /dev/null
    if [ $? -ne 0 ]
    then
        echo "删除 Milvus 容器失败。"
        exit 1
    fi
    echo "删除 Milvus 容器成功。"
}

delete() {
    read -p "确认删除吗？这将删除容器和所有数据。(y/n): " check
    if [ "$check" == "y" ] ||[ "$check" == "Y" ];then
        delete_container
        rm -rf $(pwd)/volumes
        rm -rf $(pwd)/embedEtcd.yaml
        rm -rf $(pwd)/user.yaml
        echo "✅ 删除成功。"
    else
        echo "取消删除"
        exit 0
    fi
}

case $1 in
    restart)
        stop
        start
        ;;
    start)
        start
        ;;
    stop)
        stop
        ;;
    delete)
        delete
        ;;
    *)
        echo "用法: bash standalone_embed.sh [start|stop|restart|delete]"
        ;;
esac
