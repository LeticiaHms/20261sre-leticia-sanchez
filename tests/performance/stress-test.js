import http from 'k6/http';
import { check, sleep } from 'k6';

// Teste de Estresse (Stress Test) - Identificar ponto de quebra
export const options = {
    stages: [
        { duration: '10s', target: 100 }, // Sobe para 100 VUs
        { duration: '30s', target: 100 },
        { duration: '10s', target: 200 }, // Sobe para 200 VUs (Estresse)
        { duration: '30s', target: 200 },
        { duration: '10s', target: 0 },   // Recuperação
    ],
    thresholds: {
        http_req_duration: ['p(95)<2000'], // Tolerância maior em estresse (2s)
        http_req_failed: ['rate<0.05'],   // Aceitamos até 5% de erro sob extremo estresse
    },
};

export default function () {
    const res = http.get('http://localhost:8501/');
    check(res, {
        'status is 200': (r) => r.status === 200,
    });
    sleep(1);
}
