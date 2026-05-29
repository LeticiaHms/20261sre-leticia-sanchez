import http from 'k6/http';
import { check, sleep } from 'k6';

// Teste de Carga (Load Test) - Valida RNF-05 (Disponibilidade e Performance Frontend)
export const options = {
    stages: [
        { duration: '10s', target: 50 }, // Ramp-up para 50 VUs (Virtual Users)
        { duration: '30s', target: 50 }, // Mantém carga de 50 VUs
        { duration: '10s', target: 0 },  // Ramp-down para 0 VUs
    ],
    thresholds: {
        http_req_duration: ['p(95)<500'], // 95% das requisições devem ocorrer em < 500ms
        http_req_failed: ['rate<0.01'],   // Taxa de erro < 1%
    },
};

export default function () {
    // Tática de Observabilidade: Verificação do health check
    const healthRes = http.get('http://localhost:8501/_stcore/health');
    check(healthRes, {
        'health is status 200': (r) => r.status === 200,
    });

    // Acesso à Home Page (Dashboard)
    const res = http.get('http://localhost:8501/');
    check(res, {
        'homepage is status 200': (r) => r.status === 200,
    });

    sleep(1);
}
