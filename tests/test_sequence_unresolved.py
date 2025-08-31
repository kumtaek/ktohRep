import sqlite3
import shutil
from pathlib import Path
from visualize.builders.sequence_diagram import build_sequence_graph_json


def test_sequence_diagram_includes_unknown_for_unresolved_calls(tmp_path):
    src_db = Path('PROJECT/sampleSrc/data/metadata.db')
    test_db = tmp_path / 'metadata.db'
    shutil.copy(src_db, test_db)

    conn = sqlite3.connect(test_db)
    cur = conn.cursor()
    cur.execute(
        """SELECT m.method_id, f.path FROM methods m
               JOIN classes c ON m.class_id = c.class_id
               JOIN files f ON c.file_id = f.file_id
               LIMIT 1"""
    )
    method_id, file_path = cur.fetchone()
    cur.execute(
        """INSERT INTO edges (project_id, src_type, src_id, dst_type, dst_id, edge_kind, confidence)
            VALUES (1, 'method', ?, 'method', NULL, 'call_unresolved', 0.5)""",
        (method_id,)
    )
    conn.commit()
    conn.close()

    config = {
        'database': {
            'project': {
                'type': 'sqlite',
                'sqlite': {
                    'path': str(test_db),
                    'wal_mode': True
                }
            }
        }
    }

    sequence_data = build_sequence_graph_json(
        config,
        project_id=1,
        project_name=None,
        start_file=file_path,
        start_method=None,
        depth=1,
        max_nodes=10
    )

    participants = sequence_data.get('participants', [])
    interactions = sequence_data.get('interactions', [])

    unknown_ids = [p['id'] for p in participants if p['type'] == 'unknown']
    assert unknown_ids, 'Unresolved calls should create unknown participant'
    assert any(i['to_participant'] in unknown_ids for i in interactions)