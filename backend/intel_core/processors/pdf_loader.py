from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from intel_core.utils.processing import process_pdfs
import os
import logging

# Set up logging
logger = logging.getLogger("pdf_loader")

# class Document:
#     def __init__(self, content, metadata=None, lemmatized_text=None):
#         self.page_content = content
#         self.metadata = metadata or {"title": ""}
#         self.lemmatized_text = lemmatized_text or content

#     @property
#     def title(self):
#         return self.metadata.get("title", "No Title")


def load_pdfs(
    file_paths, user_provided_title=None, project_name="General", session_id=None
):
    """
    Load and process PDFs from the given file paths.

    Args:
        file_paths (list): List of PDF file paths.
        user_provided_title (str, optional): Title to assign to the PDFs. If None,
                                            filename will be used.
        project_name (str): Name of the project for metadata.
        session_id (str): UUID of the session for tracking.

    Returns:
        list: List of processed Document objects.
    """
    logger.info(f"Loading {len(file_paths)} PDFs for project '{project_name}'")
    if session_id:
        logger.info(f"Using session_id: {session_id}")

    processed_documents = []
    for file_path in file_paths:
        try:
            # Extract filename for title if not provided
            file_name = os.path.basename(file_path)
            pdf_title = user_provided_title or os.path.splitext(file_name)[0]

            logger.info(f"Processing PDF: {pdf_title} from {file_path}")

            # Load the PDF
            loader = PDFPlumberLoader(file_path=file_path)
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=200
            )

            # Split the PDF into chunks and process each chunk
            pdf_list = loader.load_and_split(text_splitter)

            if not pdf_list or len(pdf_list) == 0:
                logger.warning(f"No content extracted from PDF: {file_path}")
                continue

            logger.info(f"Successfully extracted {len(pdf_list)} chunks from PDF")

            # Process each chunk
            for i, pdf in enumerate(pdf_list):
                # Enhance metadata
                pdf.metadata.update(
                    {
                        "title": pdf_title,
                        "source_type": "PDF",
                        "source_path": file_path,
                        "project": project_name,
                        "session_id": session_id,
                        "chunk_index": i,
                        "total_chunks": len(pdf_list),
                    }
                )

                # Process the PDF document
                processed_document = process_pdfs(
                    pdf, pdf_title, project_name, session_id
                )

                if not processed_document:
                    logger.info(
                        f"Retrying chunk {i+1}/{len(pdf_list)} for '{pdf_title}'"
                    )
                    processed_document = process_pdfs(
                        pdf, pdf_title, project_name, session_id
                    )

                if processed_document:
                    processed_documents.append(processed_document)
                    logger.info(f"Successfully processed chunk {i+1}/{len(pdf_list)}")
                else:
                    logger.error(
                        f"Failed to process chunk {i+1}/{len(pdf_list)} for '{pdf_title}'",
                        exc_info=True,
                    )

        except Exception as e:
            logger.error(f"Failed to process PDF {file_path}: {e}")
            # Continue with other PDFs even if one fails

    logger.info(f"Completed processing {len(processed_documents)} PDF chunks")
    return processed_documents
