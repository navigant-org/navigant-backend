# Navigant Backend API Documentation

Base URL: `http://127.0.0.1:5000/api`

## Authentication

### Login

- **Endpoint**: `/auth/login`
- **Method**: `POST`
- **Description**: Authenticates a user and returns a JWT token.
- **Request Body**:
  ```json
  {
    "email": "admin@navigant.com",
    "password": "password123"
  }
  ```
- **Response (200)**:
  ```json
  {
    "token": "eyJ0eXAi...",
    "user": {
      "id": 1,
      "name": "Admin User",
      "email": "admin@navigant.com"
    }
  }
  ```

### Register Admin

- **Endpoint**: `/auth/register-admin`
- **Method**: `POST`
- **Description**: Registers a new admin user.
- **Request Body**:
  ```json
  {
    "name": "Admin User",
    "email": "admin@navigant.com",
    "phone": "1234567890",
    "password": "password123"
  }
  ```
- **Response (201)**:
  ```json
  {
    "message": "Admin user registered successfully",
    "user": { ... }
  }
  ```

---

## Main (Localization)

### Welcome

- **Endpoint**: `/`
- **Method**: `GET`
- **Response (200)**:
  ```json
  {
    "message": "Navigant Backend API",
    "version": "v1"
  }
  ```

### Create Fingerprint (Training Data)

- **Endpoint**: `/fingerprint`
- **Method**: `POST`
- **Headers**: `Authorization: Bearer <token>`
- **Description**: Uploads magnetic field readings for a specific node to train the model.
- **Request Body**:
  ```json
  {
    "node_id": 1,
    "readings": [
      { "mag_x": 10.5, "mag_y": 20.1, "mag_z": 30.2 },
      { "mag_x": 10.6, "mag_y": 20.2, "mag_z": 30.1 },
      ...
    ]
  }
  ```
- **Response (201)**:
  ```json
  {
    "message": "Fingerprint created successfully"
  }
  ```

### Localize

- **Endpoint**: `/localize`
- **Method**: `POST`
- **Description**: Predicts the current node based on magnetic field readings.
- **Request Body**:
  ```json
  {
    "readings": [
      { "mag_x": 10.5, "mag_y": 20.1, "mag_z": 30.2 },
      ...
    ]
  }
  ```
- **Response (200)**:
  ```json
  {
    "predicted_node_id": 1
  }
  ```

### Get Shortest Path

- **Endpoint**: `/path`
- **Method**: `GET`
- **Description**: Computes the shortest path between two nodes on a given floor using the internal graph.
- **Request Body**:
  ```json
  {
    "start_node_id": 1,
    "end_node_id": 10,
    "floor_id": 2
  }
  ```
- **Response (200)**:

  ```json
  {
    "total_distance": 42.3,
    "path": [1, 3, 7, 10],
    "path_details": [
      {
        "node_id": 1,
        "name": "Room 101",
        "x_coordinate": 10.0,
        "y_coordinate": 20.0,
        "node_type": "room",
        "floor_id": 2
      }
    ]
  }
  ```

  - **Response (404)**:

  ```json
  {
    "message": "No path found between the specified nodes"
  }
  ```

---

## Buildings

### Get All Buildings

- **Endpoint**: `/buildings/`
- **Method**: `GET`
- **Response (200)**:
  ```json
  {
    "buildings": [
      {
        "building_id": 1,
        "name": "Engineering Block",
        "description": "...",
        "created_at": "2023-01-01T12:00:00"
      }
    ],
    "count": 1
  }
  ```

### Create Building

- **Endpoint**: `/buildings/`
- **Method**: `POST`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "name": "Engineering Block",
    "description": "Main engineering department building"
  }
  ```
- **Response (201)**: Returns created building object.

### Get Building Details

- **Endpoint**: `/buildings/<id>`
- **Method**: `GET`

### Update Building

- **Endpoint**: `/buildings/<id>`
- **Method**: `PUT`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body** (fields are optional):
  ```json
  {
    "name": "Updated Name",
    "description": "Updated Description"
  }
  ```

### Delete Building

- **Endpoint**: `/buildings/<id>`
- **Method**: `DELETE`
- **Headers**: `Authorization: Bearer <token>`

### Get Building Sub-resources

- **Get Floors**: `GET /buildings/<id>/floors`
- **Get Nodes**: `GET /buildings/<id>/nodes`
- **Get Edges**: `GET /buildings/<id>/edges`
- **Get Full Graph**: `GET /buildings/<id>/graph` (Returns nodes and edges for the building)

---

## Floors

### Create Floor

- **Endpoint**: `/floors/`
- **Method**: `POST`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "building_id": 1,
    "floor_number": 1,
    "map_img_url": "http://example.com/map.png",
    "scale": 1.5, // Optional, default 1.0
    "origin_x": 0.0, // Optional, default 0.0
    "origin_y": 0.0 // Optional, default 0.0
  }
  ```

### Get Floor

- **Endpoint**: `/floors/<id>`
- **Method**: `GET`

### Update Floor

- **Endpoint**: `/floors/<id>`
- **Method**: `PUT`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**: Any of the create fields.

### Delete Floor

- **Endpoint**: `/floors/<id>`
- **Method**: `DELETE`
- **Headers**: `Authorization: Bearer <token>`

### Get Floor Nodes

- **Endpoint**: `/floors/<id>/nodes`
- **Method**: `GET`
- **Description**: Returns all nodes that belong to the specified floor.

### Get Floor Edges

- **Endpoint**: `/floors/<id>/edges`
- **Method**: `GET`
- **Description**: Returns all edges that belong to the specified floor.

### Get Floor Graph

- **Endpoint**: `/floors/<id>/graph`
- **Method**: `GET`
- **Description**: Returns the graph for a floor, including nodes, edges, and scale information.

---

## Nodes

### Create Node

- **Endpoint**: `/nodes/`
- **Method**: `POST`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "name": "Room 101",
    "floor_id": 1,
    "x_coordinate": 10.0,
    "y_coordinate": 20.0,
    "node_type": "room" // e.g., "room", "corridor", "stairs"
  }
  ```

### Get Node

- **Endpoint**: `/nodes/<id>`
- **Method**: `GET`

### Update Node

- **Endpoint**: `/nodes/<id>`
- **Method**: `PUT`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**: Any of the create fields.

### Delete Node

- **Endpoint**: `/nodes/<id>`
- **Method**: `DELETE`
- **Headers**: `Authorization: Bearer <token>`

### Get Node Fingerprints

- **Endpoint**: `/nodes/<id>/fingerprints`
- **Method**: `GET`
- **Description**: Returns the statistical fingerprint data stored for this node.

---

## Edges

### Create Edge

- **Endpoint**: `/edges/`
- **Method**: `POST`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "start_node_id": 1,
    "end_node_id": 2,
    "distance": 5.0,
    "floor_id": 1
  }
  ```

### Get Edge

- **Endpoint**: `/edges/<id>`
- **Method**: `GET`

### Update Edge

- **Endpoint**: `/edges/<id>`
- **Method**: `PUT`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**: Any of the create fields.

### Delete Edge

- **Endpoint**: `/edges/<id>`
- **Method**: `DELETE`
- **Headers**: `Authorization: Bearer <token>`
