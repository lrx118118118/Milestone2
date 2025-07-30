from flask import Blueprint, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

api_bp = Blueprint('api', __name__)

DB_CONFIG = {
    'host': 'localhost',
    'database': 'Globalbridge',
    'user': 'postgres',
    'password': '118118',
    'port': 5432
}

@contextmanager
def get_db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()


@api_bp.route('/api/jobs', methods=['GET'])
def get_all_jobs():
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM jobs ORDER BY created_at DESC;")
            jobs = cur.fetchall()
            return jsonify({'data': jobs})


@api_bp.route('/api/jobs/<int:job_id>', methods=['GET'])
def get_job_by_id(job_id):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM jobs WHERE id = %s;", (job_id,))
            job = cur.fetchone()
            if job:
                return jsonify({'data': job})
            else:
                return jsonify({'error': 'Job not found'}), 404


@api_bp.route('/api/jobs', methods=['POST'])
def create_job():
    data = request.get_json()
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO jobs (title, company, location, visa_sponsorship, description)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING *;
            """, (
                data['title'],
                data['company'],
                data['location'],
                data['visa_sponsorship'],
                data['description']
            ))
            new_job = cur.fetchone()
            conn.commit()
            return jsonify({'message': 'Job created successfully', 'data': new_job}), 201


@api_bp.route('/api/jobs/<int:job_id>', methods=['PUT'])
def update_job(job_id):
    data = request.get_json()
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                UPDATE jobs
                SET title = %s,
                    company = %s,
                    location = %s,
                    visa_sponsorship = %s,
                    description = %s
                WHERE id = %s
                RETURNING *;
            """, (
                data['title'],
                data['company'],
                data['location'],
                data['visa_sponsorship'],
                data['description'],
                job_id
            ))
            updated_job = cur.fetchone()
            if updated_job:
                conn.commit()
                return jsonify({'message': 'Job updated successfully', 'data': updated_job})
            else:
                return jsonify({'error': 'Job not found'}), 404


@api_bp.route('/api/jobs/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM jobs WHERE id = %s RETURNING id;", (job_id,))
            deleted = cur.fetchone()
            if deleted:
                conn.commit()
                return jsonify({'message': f'Job with id {job_id} deleted.'}), 200
            else:
                return jsonify({'error': f'Job with id {job_id} not found.'}), 404




