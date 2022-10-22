# Build a CRUD API

### **[Link](https://catalog.us-east-1.prod.workshops.aws/workshops/2c8321cb-812c-45a9-927d-206eea3a500f/en-US/080-test-your-api)**
<br>

## Test the API

1. In Postman paste the invoke URL from the Output of SAM application
2. To create new item, select PUT and type this in Body section (raw-JSON):
```
{
    "price": "12345",
    "id": "markovick",
    "name": "myitem"
}
```
3. To list all items select GET and no Body
4. To list a particular item, add {item_id} to invoke URL.<br>
Example: ...com/items/markovick
5. To delete a item, add {item_id} to invoke URL.<br>
Example: ...com/items/markovick