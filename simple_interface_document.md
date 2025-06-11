## 1. Cost Estimation Module 

> localhost:8000/estimate/empirical/cocomo

```json
{
  "size": 50,
  "complexity": "semi"
}
```



> localhost:8000/estimate/empirical/fpa

```json
{
  "size": 50,
  "complexity": "organic"
}
```



> localhost:8000/estimate/heuristic/expert

```json
{
  "size": 60,
  "experience": 3
}
```



> localhost:8000/estimate/heuristic/delphi

```json
{
  "size": 55,
  "experience_list": [1,2,3,4]
}
```



> localhost:8000/estimate/mathematical/regression

```json
{
  "method": "regression",
  "size": 510,
  "complexity": "medium",
  "experience": 3,
  "historical_data": [
    [
        1,
        2
    ],
    [
        3,
        9
    ]
  ]
}
```





------

## 2. Budgeting and Cost Management 

> localhost:8000/cost/roi

```json
{
  "gain": 20,
  "cost": 10
}
```



> localhost:8000/cost/npv

```json
{
  "cash_flows": [
    1, 2, 4
  ],
  "discount_rate": 0.6
}
```



> localhost:8000/cost/irr

```json
{
  "cash_flows": [-1000, 200, 300, 400, 500]
}
```



> localhost:8000/cost/pp

```json
{
  "cash_flows": [-1000, 200, 300, 400, 500]
}

```



> localhost:8000/cost/forecast

```json
{
  "historical_data": [1,2,4,5,10],
  "future_periods": 5
}

```





------

## 3. Risk Management Module 



> localhost:8000/decision-tree/sensitivity

```json
{
  "tree": {
    "name": "Choose Project",
    "children": [
      {
        "name": "Dev A",
        "children": [
          {
            "name": "A Success",
            "value": 100,
            "probability": 0.7
          },
          {
            "name": "A Failure",
            "value": -20,
            "probability": 0.3
          }
        ]
      }
    ]
  },
  "target_path": [
    "Dev A",
    "A Success"
  ],
  "field": "probability",
  "range": {
    "start": 0.6,
    "end": 0.9,
    "step": 0.05
  }
}

```





> localhost:8000/decision-tree/sensitivity/multi

```json
{
  "tree": {
    "name": "Choose Project",
    "children": [
      {
        "name": "Dev A",
        "children": [
          {
            "name": "A Success",
            "value": 100,
            "probability": 0.7
          },
          {
            "name": "A Failure",
            "value": -20,
            "probability": 0.3
          }
        ]
      },
      {
        "name": "Dev B",
        "children": [
          {
            "name": "B Success",
            "value": 150,
            "probability": 0.5
          },
          {
            "name": "B Failure",
            "value": -40,
            "probability": 0.5
          }
        ]
      }
    ]
  },
  "fields": [
    {
      "target_path": [
        "Dev A",
        "A Success"
      ],
      "field": "probability",
      "range": {
        "start": 0.6,
        "end": 0.9,
        "step": 0.1
      }
    },
    {
      "target_path": [
        "Dev B",
        "B Success"
      ],
      "field": "probability",
      "range": {
        "start": 0.4,
        "end": 0.7,
        "step": 0.1
      }
    }
  ]
}

```



> localhost:8000/decision-tree/evaluate

```json
{
  "name": "Choose Project",
  "children": [
    {
      "name": "Dev A",
      "children": [
        {
          "name": "A Success",
          "value": 100,
          "probability": 0.7
        },
        {
          "name": "A Failure",
          "value": -20,
          "probability": 0.3
        }
      ]
    },
    {
      "name": "Dev B",
      "children": [
        {
          "name": "B Success",
          "value": 150,
          "probability": 0.5
        },
        {
          "name": "B Failure",
          "value": -40,
          "probability": 0.5
        }
      ]
    }
  ]
}

```





> localhost:8000/decision-tree/monte-carlo

```json
{
  "tree": {
    "name": "Choose Project",
    "children": [
      {
        "name": "Dev A",
        "children": [
          {
            "name": "A Success",
            "value": 100,
            "probability": 0.7
          },
          {
            "name": "A Failure",
            "value": -20,
            "probability": 0.3
          }
        ]
      }
    ]
  },
  "target_path": [
    "Dev A",
    "A Success"
  ],
  "field": "value",
  "distribution": "normal",
  "params": {
    "mean": 100,
    "stddev": 15
  },
  "runs": 1000,
  "bins": 10
}

```









------

## 4. Resource Allocation & Optimization  

> localhost:8000/resource/smoothing
>
> localhost:8000/resource/leveling

```json
{
  "activities": [
    {
      "name": "A",
      "duration": 4,
      "resource": 4,
      "predecessors": []
    },
    {
      "name": "B",
      "duration": 3,
      "resource": 3,
      "predecessors": ["A"]
    },
    {
      "name": "C",
      "duration": 5,
      "resource": 2,
      "predecessors": ["A"]
    },
    {
      "name": "D",
      "duration": 2,
      "resource": 5,
      "predecessors": ["B"]
    },
    {
      "name": "E",
      "duration": 3,
      "resource": 1,
      "predecessors": ["B", "C"]
    },
    {
      "name": "F",
      "duration": 4,
      "resource": 3,
      "predecessors": ["D"]
    },
    {
      "name": "G",
      "duration": 2,
      "resource": 2,
      "predecessors": ["E"]
    },
    {
      "name": "H",
      "duration": 3,
      "resource": 4,
      "predecessors": ["F", "G"]
    }
  ],
  "resource_limit": 7
}


```



