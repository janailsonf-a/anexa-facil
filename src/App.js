import React, { useState, useEffect, useRef } from 'react';
import imageCompression from 'browser-image-compression'; // 1. Importamos a nova biblioteca

function App() {
    const [boleto, setBoleto] = useState(null);
    const [comprovante, setComprovante] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [previewUrl, setPreviewUrl] = useState(null);

    const boletoInputRef = useRef(null);
    const comprovanteInputRef = useRef(null);

    const handleClear = () => {
        setBoleto(null);
        setComprovante(null);
        setSuccess('');
        setError('');
        setPreviewUrl(null);
        if (boletoInputRef.current) {
            boletoInputRef.current.value = null;
        }
        if (comprovanteInputRef.current) {
            comprovanteInputRef.current.value = null;
        }
    };

    // 2. A função agora é 'async' para esperar a compressão
    const handleComprovanteChange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        console.log(`Tamanho original da imagem: ${(file.size / 1024 / 1024).toFixed(2)} MB`);

        const options = {
            maxSizeMB: 1, // Tamanho máximo do arquivo em MB
            maxWidthOrHeight: 1920, // Redimensiona se for maior que 1920px
            useWebWorker: true, // Usa processamento paralelo para ser mais rápido
        };

        try {
            // 3. Chamamos a função de compressão
            const compressedFile = await imageCompression(file, options);
            console.log(`Tamanho da imagem comprimida: ${(compressedFile.size / 1024 / 1024).toFixed(2)} MB`);

            // 4. Usamos o arquivo comprimido para o resto do processo
            setComprovante(compressedFile);
            if (previewUrl) {
                URL.revokeObjectURL(previewUrl);
            }
            setPreviewUrl(URL.createObjectURL(compressedFile));

        } catch (error) {
            console.error("Erro ao comprimir a imagem:", error);
            setError("Não foi possível processar a imagem selecionada.");
        }
    };

    useEffect(() => {
        return () => {
            if (previewUrl) {
                URL.revokeObjectURL(previewUrl);
            }
        };
    }, [previewUrl]);

    const boletoFileName = boleto ? boleto.name : "Nenhum arquivo selecionado";
    const comprovanteFileName = comprovante ? comprovante.name : "Nenhum arquivo selecionado";

    const handleSubmit = async (event) => {
        event.preventDefault();
        if (!boleto || !comprovante) {
            setError('Por favor, anexe os dois arquivos.');
            return;
        }
        setIsLoading(true);
        setError('');
        setSuccess('');
        const formData = new FormData();
        formData.append('boleto', boleto);
        formData.append('comprovante', comprovante);
        try {
            const response = await fetch('/api/process', {
                method: 'POST',
                body: formData,
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Ocorreu um erro no servidor.');
            }
            let downloadFilename = 'comprovante_final.pdf';
            const disposition = response.headers.get('Content-Disposition');
            if (disposition && disposition.indexOf('attachment') !== -1) {
                const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
                const matches = filenameRegex.exec(disposition);
                if (matches != null && matches[1]) {
                    downloadFilename = matches[1].replace(/['"]/g, '');
                }
            }
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = downloadFilename;
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
            setSuccess('PDF gerado e baixado com sucesso!');
        } catch (err) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        // O JSX continua o mesmo
        <div className="bg-slate-900 min-h-screen flex items-center justify-center p-4">
            <div className="bg-slate-800 p-8 rounded-2xl shadow-2xl w-full max-w-lg">
                <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-500 text-center mb-4">
                    Anexa Fácil
                </h1>
                <p className="text-slate-300 text-center text-lg mb-10">
                    Faça o upload dos seus arquivos para criar um comprovante de pagamento unificado.
                </p>

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="text-left">
                        <label className="font-semibold text-slate-300 mb-2 block">1. Selecione o Boleto (.pdf)</label>
                        <label htmlFor="boleto-upload" className="cursor-pointer bg-slate-700 text-slate-300 p-3 rounded-lg w-full flex items-center justify-between hover:bg-slate-600 transition">
                            <span className="truncate max-w-xs">{boletoFileName}</span>
                            <span className="bg-blue-600 text-white font-bold py-1 px-3 rounded-md">Escolher</span>
                        </label>
                        <input id="boleto-upload" type="file" accept=".pdf" className="hidden" ref={boletoInputRef} onChange={(e) => setBoleto(e.target.files[0])} />
                    </div>

                    <div className="text-left">
                        <label className="font-semibold text-slate-300 mb-2 block">2. Selecione o Comprovante (imagem)</label>
                        {previewUrl && (
                            <div className="my-4">
                                <img src={previewUrl} alt="Pré-visualização do Comprovante" className="max-h-40 rounded-lg mx-auto" />
                            </div>
                        )}
                        <label htmlFor="comprovante-upload" className="cursor-pointer bg-slate-700 text-slate-300 p-3 rounded-lg w-full flex items-center justify-between hover:bg-slate-600 transition">
                            <span className="truncate max-w-xs">{comprovanteFileName}</span>
                            <span className="bg-blue-600 text-white font-bold py-1 px-3 rounded-md">Escolher</span>
                        </label>
                        <input id="comprovante-upload" type="file" accept="image/*" className="hidden" ref={comprovanteInputRef} onChange={handleComprovanteChange} />
                    </div>

                    <div className="space-y-4 pt-4">
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full font-bold text-lg text-white bg-gradient-to-r from-blue-600 to-indigo-600 p-4 rounded-lg shadow-lg hover:scale-105 transition transform duration-300 disabled:bg-slate-600 disabled:hover:scale-100 disabled:cursor-not-allowed"
                        >
                            {isLoading ? 'Processando...' : 'Juntar e Baixar PDF'}
                        </button>
                        { (boleto || comprovante) && !isLoading && (
                            <button
                                type="button"
                                onClick={handleClear}
                                className="w-full font-semibold text-red-500 border border-red-500 p-2 rounded-lg hover:bg-red-500 hover:text-white transition duration-300"
                            >
                                Limpar Seleção
                            </button>
                        )}
                    </div>
                </form>

                {error && <p className="text-red-400 font-semibold mt-4">{error}</p>}
                {success && <p className="text-green-500 font-semibold mt-4">{success}</p>}

                {/* Rodapé de Copyright */}
                <footer className="text-center text-xs text-slate-500 pt-6 mt-6 border-t border-slate-700">
                    <p>&copy; 2025 <a href="https://github.com/janailsonf-a" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">Janailson Firmino de Almeida</a>. Todos os direitos reservados.</p>
                </footer>
            </div>

        </div>

    );


}

export default App;