# should define datas for replacement in a tamplate to debug it

data = {
    "environment": {
        "outputs": {
            "PublicSubnetOne": "sub1",
            "PublicSubnetTwo": "sub2",
            "VpcId": "VpcId"
        }
    },
    "service": {
        "name": "service-name"
    },
    "service_instance": {
        "name": "service_instance-name",
        "inputs": {
            "instance_size": "x-small",
            "manage_accountid": "12345"
        }
    },
    "pipeline": {
        "inputs": {
            "environment_accountid": "12345"
        }
    },
    "service_instances": [
        {
            "name": "service_instance-name",
            "inputs": {
                "instance_size": "x-small"
            },
            "outputs": {
                "Region": "Region",
                "AMIBaseEC2": "AMIBaseEC2",
                "LaunchTemplate": "LaunchTemplate",
                "DeployAccountRoleArn": "DeployAccountRoleArn",
                "AutoScalingName": "AutoScalingName",
            }
        }
    ]
}
