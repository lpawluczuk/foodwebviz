from conftest import BOUNDARIES, FLOWS


def test_init_foodweb(food_web):
    assert food_web.n == 3
    assert food_web.n_living == 2
    assert food_web.get_links_number() == 4


def test_getFlowMatWithBoundary(food_web):
    flow_matrix_with_boundary = food_web.get_flow_matrix(boundary=True)

    assert all(col in flow_matrix_with_boundary.columns for col in BOUNDARIES)
    assert all(col in flow_matrix_with_boundary.index for col in BOUNDARIES)

    for b in BOUNDARIES:
        assert flow_matrix_with_boundary[b].loc[b] == 0.0


def test_graph(food_web, processed_node_df):
    web_nodes = dict(food_web._graph.nodes(data=True))
    for b in BOUNDARIES:
        processed_node_df[b] = {}

    assert web_nodes == processed_node_df
    assert list(food_web._graph.edges(data=True)) == FLOWS


def test_get_graph(food_web, processed_node_df):
    # no boundaries
    web_nodes = food_web.get_graph(boundary=False, mark_alive_nodes=False).nodes()
    test_nodes = processed_node_df.keys()
    assert list(web_nodes) == list(test_nodes)

    # with boundaries
    web_nodes = food_web.get_graph(boundary=True, mark_alive_nodes=False).nodes()
    assert list(web_nodes) == list(test_nodes) + BOUNDARIES

    # with not alive marks
    web_nodes = food_web.get_graph(boundary=False, mark_alive_nodes=True).nodes()
    assert list(web_nodes) == ['A', 'B', '✗ C']


def test_get_normalized_flows(food_web):
    normalized_weights = {
        'linear': [3.0, 2.0, 2.0, 5.0],
        'tst': [0.25, 0.16666666666666666, 0.16666666666666666, 0.4166666666666667],
        'donor_control': [3.0, 2.0, 0.6666666666666666, 1.0],
        'predator_control': [1.0, 0.4, 0.4, 1.6666666666666667],
        'mixed_control': [3.0, 0.8, 0.26666666666666666, 1.6666666666666667],
        'log': [0.47712125471966244, 0.3010299956639812, 0.3010299956639812, 0.6989700043360189],
        'diet': [0.375, 0.5, 0.5, 0.625]
    }

    for norm, expected in normalized_weights.items():
        weights = [e[2]['weight'] for e in food_web.get_flows(normalization=norm)]
        assert weights == expected

    g = food_web.get_graph(boundary=True, normalization='diet')
    for node in g.nodes():
        # sum of each node's input weights should be 1
        if node != 'Import':
            assert sum([x[2] for x in g.in_edges(node, data='weight')]) == 1.0
