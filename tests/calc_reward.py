from collections import defaultdict


def set_delegate(address, value, last_claim=False):
    return {"address": address, "value": value, 'last_claim': last_claim}


def parse_delegation(agents, block_reward):
    """
    :param block_reward:
    :param agents:
        example:
        [{
            "address": 0xdasdas213123,
            "active": True,
            "coin": [{
                "address": 0x21312321389123890,
                "value: 3,
                "last_claim": true
            }, {
                "address": 0x21312321389123890,
                "value: 4
            }],
            "power": [{
                "address": 0x128381290830912,
                "value: 99
            }]
        }]
    :return: agent score dict and delegate reward dict
        example:
        {"0xdasdas213123": 33, "0x12321312312": 23}
        {"0x21312321389123890": 13, "0x21312321389123890": 3}
    """
    btc_count = 1
    coin_count = 1

    agent_score = {}
    delegator_reward = defaultdict(int)

    for agent in agents:
        agent['totalReward'] = block_reward
        agent['remainReward'] = block_reward
        total_power = sum([item['value'] for item in agent['power']])
        agent['total_power'] = total_power
        btc_count += total_power
        total_coin = sum([item['value'] for item in agent['coin']])
        agent['total_coin'] = total_coin
        coin_count += total_coin

    for agent in agents:
        agent_score[agent['address']] = 2 * agent['total_power'] * coin_count + agent['total_coin'] * btc_count

    for agent in agents:
        if not agent['active']:
            continue

        reward_each_power = coin_count * 20000 // 10000 * agent['totalReward'] // agent_score[agent['address']]
        for item in agent['power']:
            reward = item['value'] * reward_each_power
            delegator_reward[item['address']] += reward
            print(f"power reward: {agent['address']} on {item['address']} => {reward}")
            assert agent['remainReward'] >= reward
            agent['remainReward'] -= reward
        if agent['remainReward'] > 0 and list(agent.get('coin', [])) == 0 and len(agent.get('power', [])) > 0:
            delegator_reward[agent['power'][0]['address']] += agent['remainReward']
            print(f"power dust reward: {agent['power'][0]['address']} => {agent['remainReward']}")

        for item in agent['coin']:
            if item.get('last_claim', False):
                reward = agent['remainReward']
            else:
                reward = agent['totalReward'] * item['value'] * btc_count // agent_score[agent['address']]
                assert agent['remainReward'] >= reward
                agent['remainReward'] -= reward
            delegator_reward[item['address']] += reward
            print(f"coin reward: {agent['address']} on {item['address']} => {reward}")

    assert sum(delegator_reward.values()) == block_reward * len(agents)

    return agent_score, delegator_reward


if __name__ == '__main__':
    # delegate_info = [{
    #     "address": "n1",
    #     "coin": [set_delegate("x", 4), set_delegate("y", 2)],
    #     "power": [set_delegate("x", 2), set_delegate("y", 1)]
    # }, {
    #     "address": "n2",
    #     "coin": [{"address": "z", "value": 9}],
    #     "power": [{"address": "z", "value": 2}]
    # }]

    delegate_info = [{
        "address": "n0",
        "active": True,
        "coin": [set_delegate("x", 2e18)],
        "power": [set_delegate("x", 6e18)]
    }]

    _agent_score, _delegator_reward = parse_delegation(delegate_info, 324000000)
    print(_agent_score)
    print(_delegator_reward)
