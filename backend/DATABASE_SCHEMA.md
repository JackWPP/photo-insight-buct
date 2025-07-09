# 数据库表结构说明 (v0.2)

本文档详细说明了 `PhotoInsight` 项目 v0.2 版本中使用的 SQLite 数据库的表结构。数据库的核心设计分为一个主图片信息表和四个独立的季节关联表。

## 主表: `images`

该表是项目的核心，用于存储所有被索引图片的基础元数据，并关联到其在向量数据库中的特征向量。

### 字段详情

| 字段名       | 数据类型          | 约束                | 描述                                                               |
|--------------|-------------------|---------------------|--------------------------------------------------------------------|
| `id`         | `INTEGER`         | `PRIMARY KEY`       | 表的唯一主键，自增。                                               |
| `path`       | `VARCHAR`         | `UNIQUE`, `NOT NULL`| 图片文件的绝对路径。这是识别文件的核心字段，具有唯一性。           |
| `filename`   | `VARCHAR`         | `NOT NULL`          | 图片的文件名（例如 `photo.jpg`）。                                 |
| `size_mb`    | `FLOAT`           | `NOT NULL`          | 图片文件的大小，单位为 MB。                                        |
| `created_at` | `DATETIME`        | `DEFAULT (now)`     | 图片文件的原始创建时间或记录创建时间。                             |
| `indexed_at` | `DATETIME`        | `DEFAULT (now)`     | 该记录被添加到数据库的时间戳。                                     |
| `vector_id`  | `VARCHAR`         | `UNIQUE`, `NULLABLE`| 图片在向量数据库 (ChromaDB) 中的唯一ID。通常是一个UUID字符串。如果此字段为NULL，表示该图片尚未被AI模型处理。 |

### 索引

- `ix_images_id`: 主键索引。
- `ix_images_path`: `path` 字段的唯一索引，用于快速通过文件路径查询，并防止重复索引。
- `ix_images_vector_id`: `vector_id` 字段的唯一索引。

---

## 季节关联表

为了实现对图片季节的分类存储，项目采用了四个独立的关联表。当一张图片被AI识别为属于某个季节时，会在对应的季节表中创建一条记录，通过外键 `image_id` 指向 `images` 表中的主记录。

这种设计的优点是查询特定季节的图片时效率高，且结构清晰。

### 表: `spring_photos`, `summer_photos`, `autumn_photos`, `winter_photos`

这四个表的结构完全相同，以 `spring_photos` 为例：

| 字段名    | 数据类型  | 约束                               | 描述                                     |
|-----------|-----------|------------------------------------|------------------------------------------|
| `id`      | `INTEGER` | `PRIMARY KEY`                      | 关联表自身的唯一主键。                   |
| `image_id`| `INTEGER` | `FOREIGN KEY (images.id)`, `UNIQUE`| 指向 `images` 表中对应图片记录的外键。   |

**关系:**
- `spring_photos.image_id` -> `images.id`
- `summer_photos.image_id` -> `images.id`
- `autumn_photos.image_id` -> `images.id`
- `winter_photos.image_id` -> `images.id`
