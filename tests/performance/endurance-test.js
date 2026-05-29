import http from 'k6/http';
import { check, sleep } from 'k6';

// Endurance Test - Validar estabilidade sob carga contínua por longo período
export const options = {
    stages: [
        { duration: '10s', target: 50 },  // Ramp-up
        { duration: '2m', target: 50 },   // Mantém por 2 minutos (tempo reduzido para o lab, num cenário real seriam horas)
        { duration: '10s', target: 0 },   // Ramp-down
    ],
    thresholds: {
        http_req_duration: ['p(95)<500'], // Não deve haver degradação de performance ao longo do tempo
        http_req_failed: ['rate<0.01'],   // Menos de 1% de erro
    },
};

export default function () {
    const res = http.get('http://localhost:8501/');
    check(res, {
        'status is 200': (r) => r.status === 200,
    });
    sleep(1);
}
