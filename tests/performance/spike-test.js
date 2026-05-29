import http from 'k6/http';
import { check, sleep } from 'k6';

// Spike Test - Validar comportamento sob pico repentino de acessos
export const options = {
    stages: [
        { duration: '5s', target: 20 },   // Carga normal baixa
        { duration: '10s', target: 300 }, // PICO repentino (300 VUs)
        { duration: '15s', target: 300 }, // Mantém o pico brevemente
        { duration: '10s', target: 20 },  // Desce rápido (recuperação)
        { duration: '10s', target: 0 },
    ],
    thresholds: {
        http_req_failed: ['rate<0.05'], // Tolerância ao pico
    },
};

export default function () {
    const res = http.get('http://localhost:8501/');
    check(res, {
        'status is 200': (r) => r.status === 200,
    });
    sleep(1);
}
