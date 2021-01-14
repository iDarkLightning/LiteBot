# LiteBot API

LiteBot now runs a webserver that has support for API endpoints! In order to make a request to one of these endpoints,
anyone with the administrator permission can generate an API token for themselves using the `token` command.

## Usage
In order to make a request, you must include your token in the the headers when making the request.

**Example Header**
```python
{Authorization: "Bearer token"}
```

## Available Endpoints
Currently, the following endpoints are available

* `GET /members` Returns a json with all members that have the query id.

    **Example URL**
    ```
    http://localhost:8000/members?ids=7544066453129237839,754406645777666659
    ```
    
    **Example Response**
    ```json
    {
        "members_data": [
        {
          "name": "John Doe",
          "discriminator": "#3001",
          "id": 7524034451325937659
        },
        {
          "name": "Little Rabbit",
          "discriminator": "#9002",
          "id": 75240344534125937659
        }  
      ]
    }
    ```

