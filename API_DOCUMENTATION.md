BATTLESIM API Documentation

BASE URL: [Your server's base URL]

API Endpoint: /run_simulation

Description:
This API endpoint simulates small-scale military battles using agent-based modeling. It allows users to specify the number of soldiers, medics, and mines, and returns the final statistics of the simulation.

Method: GET

URL Parameters:
- n_soldiers (Integer): Optional. The number of soldier agents to be included in the simulation, reasonable value 40-100. Default is 50.
- n_medics (Integer): Optional. The number of medic agents to be included in the simulation, reasonable value 0-4. Default is 0.
- n_mines (Integer): Optional. The number of mines to be included on the battlefield,, reasonable value 0-5. Default is 1.

Response Format:
The response is a JSON object containing the final statistics of the battle simulation, such as the number of surviving agents, total damage inflicted, etc.

Example Request:
GET [Your server's base URL]/run_simulation?n_soldiers=60&n_medics=2&n_mines=3

Example Response:
```json
{
  "Number of allies alive": 30,
  "Number of enemies alive": 28,
  "Total damage by allies": 1500,
  "Total damage by enemies": 1400
}
