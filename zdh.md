# How To Run
## Auther's Info
### step 1 : get the attr_value_length for each entity in knowledge graph
> dbpedia-wiki-V1 data
> att1 : attr_num==10 attr_value_length==28 (25-30) att_kind_num=343
> att2 : attr_num==18 attr_value_length==38 att_kind_num=611
> dbpedia-wiki-V2 data
> att1 : attr_num==10 attr_value_length==40 att_kind_num=236
> att2 : attr_num==18 attr_value_length==38-40 att_kind_num=435

### step 2 : get the attr_num for each entity in knowledge graph and the att_kind_num is checked from the attr_id file.

### step 3: get the input pickle for the attribution information.

### step 4: set the parameters in attr_param.py and param.py according to above steps. and change the input file of run.py

### step 5: run run.py

# Know in advance
## Database
## Data Struct
### triples
#### 实体三元组
> entity triple (head, relation, tail)  head/tail 是实体，relation 是关系
#### 属性三元组（关系三元组）
> relation triple (head, relation, tail) head 是实体， relation 是属性， tail 是值