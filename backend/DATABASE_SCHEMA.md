# 数据库表结构说明 (v0.1)

本文档详细说明了 `PhotoInsight` 项目 v0.1 版本中使用的 SQLite 数据库的表结构。

## 数据表: `images`

该表是项目的核心，用于存储所有被索引图片的基础元数据，并关联到其在向量数据库中的特征向量。

### 字段详情

| 字段名       | 数据类型          | 约束                | 描述                                                               |
|--------------|-------------------|---------------------|--------------------------------------------------------------------|
| `id`         | `INTEGER`         | `PRIMARY KEY`       | 表的唯一主键，自增。                                               |
| `path`       | `VARCHAR`         | `UNIQUE`, `NOT NULL`| 图片文件的绝对路径。这是识别文件的核心字段，具有唯一性。           |
| `filename`   | `VARCHAR`         | `NOT NULL`          | 图片的文件名（例如 `photo.jpg`）。                                 |
| `size_mb`    | `FLOAT`           | `NOT NULL`          | 图片文件的大小，单位为 MB。                                        |
| `created_at` | `DATETIME`        |                     | 图片文件的原始创建时间��                                           |
| `indexed_at` | `DATETIME`        | `DEFAULT (now)`     | 该记录被添加到数据库的时间戳。                                     |
| `vector_id`  | `VARCHAR`         | `UNIQUE`, `NULLABLE`| 图片在向量数据库 (ChromaDB) 中的唯一ID。通常是一个UUID字符串。如果此字段为NULL，表示该图片尚未被AI模型处理。 |

### 索引

- `ix_images_id`: 主键索引，用于通过 ID 快速查询。
- `ix_images_path`: `path` 字段的唯一索引，用于快速通过文件路径查询，并防止重复索引。
- `ix_images_vector_id`: `vector_id` 字段的唯一索引，用于快速查询。

---

*注：在 v0.1 的重构中，我们决定将描述性文本（description）的管理完全交给前端或在需要时动态生成，数据库只负责存储核心元数据和向量ID。如果未来需要存储AI生成的固定描述，可以再将该字段添加回来。*