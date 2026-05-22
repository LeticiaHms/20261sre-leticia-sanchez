import uuid
import os
from common.logger import logger
from common.config import config
from ingestor.minio_client import MinioClient
from loader.bronze_loader import BronzeLoader
from loader.silver_transformer import SilverTransformer
from loader.gold_aggregator import GoldAggregator

class BatchManager:
    """Maestro responsável por orquestrar as camadas Medalhão em Batch."""

    def __init__(self):
        self.batch_id = str(uuid.uuid4())
        self.logger = logger.bind(batch_id=self.batch_id)
        self.minio = MinioClient()
        self.bronze_loader = BronzeLoader()
        self.silver_transformer = SilverTransformer(batch_id=self.batch_id)
        self.gold_aggregator = GoldAggregator()
        
        # Arquivos esperados
        self.source_files = [
            "northwind_orders.csv",
            "northwind_order_details.csv"
        ]
        self.local_spec_path = "documents/spec/"

    def run_pipeline(self):
        self.logger.info("Iniciando Pipeline Northwind", mode="Batch")
        
        try:
            # 1. Ingestão (Local -> Landing Zone / MinIO)
            self._run_ingestion()

            # 2. Camada Bronze (Landing -> Raw Ingestion Table -> Emergent Views)
            self._run_bronze_layer()

            # 3. Camada Silver (Bronze -> Silver Table)
            self._run_silver_layer()

            # 4. Camada Gold (Silver -> Gold Aggregates)
            self._run_gold_layer()

            self.logger.info("Pipeline Northwind finalizado com sucesso")

        except Exception as e:
            self.logger.critical("Falha crítica no pipeline batch", error=str(e))
            raise

    def _run_ingestion(self):
        """Mover arquivos locais para o MinIO (Landing Zone)."""
        self.logger.info("Executando Ingestão (Inbound -> Landing Zone)")
        for filename in self.source_files:
            local_path = os.path.join(self.local_spec_path, filename)
            if os.path.exists(local_path):
                self.minio.upload_file(local_path, filename)
            else:
                self.logger.warning(f"Arquivo local não encontrado: {local_path}")

    def _run_bronze_layer(self):
        """Lê do storage e grava na tabela de ingestão imutável (Append-only)."""
        self.logger.info("Executando Camada Bronze (Append-Only JSON)")
        for filename in self.source_files:
            local_path = os.path.join(self.local_spec_path, filename)
            if os.path.exists(local_path):
                self.bronze_loader.load_csv_to_raw(local_path, filename)

    def _run_silver_layer(self):
        """Transformação Bronze -> Silver (Cleaned & Unified)."""
        self.logger.info("Executando Camada Silver (Cleaned & Unified)")
        self.silver_transformer.transform_and_load()

    def _run_gold_layer(self):
        """Agregação Silver -> Gold (Business Data Marts)."""
        self.logger.info("Executando Camada Gold (Aggregates)")
        self.gold_aggregator.aggregate_and_load()

if __name__ == "__main__":
    manager = BatchManager()
    manager.run_pipeline()
