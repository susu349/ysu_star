from typing import Optional, List, Dict, Any
from pymilvus import (
    connections,
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
    utility,
)
from .config import get_settings

settings = get_settings()


class MilvusClient:
    _instance: Optional["MilvusClient"] = None
    _connected: bool = False

    def __new__(cls) -> "MilvusClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def connect(self) -> None:
        if self._connected:
            return
        connections.connect(
            alias="default",
            host=settings.MILVUS_HOST,
            port=settings.MILVUS_PORT,
        )
        self._connected = True

    def disconnect(self) -> None:
        if self._connected:
            connections.disconnect("default")
            self._connected = False

    def create_collection(
        self,
        collection_name: str,
        dimension: int,
        description: str = "",
        auto_id: bool = True,
    ) -> Collection:
        full_name = f"{settings.MILVUS_COLLECTION_PREFIX}_{collection_name}"

        if utility.has_collection(full_name):
            return Collection(full_name)

        fields = [
            FieldSchema(
                name="id",
                dtype=DataType.INT64,
                is_primary=True,
                auto_id=auto_id,
            ),
            FieldSchema(
                name="embedding",
                dtype=DataType.FLOAT_VECTOR,
                dim=dimension,
            ),
            FieldSchema(
                name="metadata",
                dtype=DataType.JSON,
            ),
        ]

        schema = CollectionSchema(
            fields=fields,
            description=description,
            enable_dynamic_field=False,
        )

        collection = Collection(name=full_name, schema=schema)

        index_params = {
            "metric_type": "IP",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 1024},
        }
        collection.create_index(field_name="embedding", index_params=index_params)

        return collection

    def get_collection(self, collection_name: str) -> Optional[Collection]:
        full_name = f"{settings.MILVUS_COLLECTION_PREFIX}_{collection_name}"
        if utility.has_collection(full_name):
            return Collection(full_name)
        return None

    def drop_collection(self, collection_name: str) -> None:
        full_name = f"{settings.MILVUS_COLLECTION_PREFIX}_{collection_name}"
        if utility.has_collection(full_name):
            utility.drop_collection(full_name)

    def insert_vectors(
        self,
        collection_name: str,
        embeddings: List[List[float]],
        metadata_list: List[Dict[str, Any]],
    ) -> List[int]:
        collection = self.get_collection(collection_name)
        if collection is None:
            collection = self.create_collection(
                collection_name,
                dimension=len(embeddings[0]) if embeddings else settings.EMBEDDING_DIMENSION,
            )

        collection.load()
        data = [embeddings, metadata_list]
        result = collection.insert(data)
        collection.flush()
        return result.primary_keys

    def search_vectors(
        self,
        collection_name: str,
        query_embedding: List[float],
        top_k: int = 10,
        filter_expr: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        collection = self.get_collection(collection_name)
        if collection is None:
            return []

        collection.load()
        search_params = {"metric_type": "IP", "params": {"nprobe": 10}}

        results = collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            expr=filter_expr,
            output_fields=["metadata"],
        )

        output = []
        for hits in results:
            for hit in hits:
                output.append({
                    "id": hit.id,
                    "score": hit.score,
                    "metadata": hit.entity.get("metadata"),
                })
        return output

    def delete_by_ids(self, collection_name: str, ids: List[int]) -> None:
        collection = self.get_collection(collection_name)
        if collection is None:
            return
        expr = f"id in [{','.join(map(str, ids))}]"
        collection.delete(expr)


def get_milvus_client() -> MilvusClient:
    client = MilvusClient()
    client.connect()
    return client
