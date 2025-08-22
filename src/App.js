import React, { useState } from 'react';

// Se você estiver usando o Tailwind, o CSS é importado pelo index.js
// Se estiver usando o App.css, descomente a linha abaixo
// import './App.css';

function App() {
    const [boleto, setBoleto] = useState(null);
    const [comprovante, setComprovante] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

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
                throw new Error('Ocorreu um erro no servidor ao processar os arquivos.');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'comprovante_final.pdf';
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
            setSuccess('PDF gerado e baixado com sucesso!');

        } catch (err) {
            setError('Falha na comunicação com o servidor. Verifique o terminal para mais detalhes.');
        } finally {
            setIsLoading(false);
        }
    };

    const boletoFileName = boleto ? boleto.name : "Nenhum arquivo selecionado";
    const comprovanteFileName = comprovante ? comprovante.name : "Nenhum arquivo selecionado";

    return (
        <div className="bg-slate-900 min-h-screen flex items-center justify-center p-4">
            <div className="bg-slate-800 p-8 rounded-2xl shadow-2xl w-full max-w-lg">

                {/* Título com gradiente e maior */}
                <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-500 text-center mb-4">
                    Anexa Fácil
                </h1>
                {/* Subtítulo com mais destaque */}
                <p className="text-slate-300 text-center text-lg mb-10">
                    Faça o upload dos seus arquivos para criar um comprovante de pagamento unificado.
                </p>

                <form onSubmit={handleSubmit} className="space-y-6">
                    {/* Seção de Upload do Boleto */}
                    <div className="text-left">
                        <label className="font-semibold text-slate-300 mb-2 block">1. Selecione o Boleto (.pdf)</label>
                        <label htmlFor="boleto-upload" className="cursor-pointer bg-slate-700 text-slate-300 p-3 rounded-lg w-full flex items-center justify-between hover:bg-slate-600 transition">
                            <span className="truncate max-w-xs">{boletoFileName}</span>
                            <span className="bg-blue-600 text-white font-bold py-1 px-3 rounded-md">Escolher</span>
                        </label>
                        <input id="boleto-upload" type="file" accept=".pdf" className="hidden" onChange={(e) => setBoleto(e.target.files[0])} />
                    </div>

                    {/* Seção de Upload do Comprovante */}
                    <div className="text-left">
                        <label className="font-semibold text-slate-300 mb-2 block">2. Selecione o Comprovante (imagem)</label>
                        <label htmlFor="comprovante-upload" className="cursor-pointer bg-slate-700 text-slate-300 p-3 rounded-lg w-full flex items-center justify-between hover:bg-slate-600 transition">
                            <span className="truncate max-w-xs">{comprovanteFileName}</span>
                            <span className="bg-blue-600 text-white font-bold py-1 px-3 rounded-md">Escolher</span>
                        </label>
                        <input id="comprovante-upload" type="file" accept="image/*" className="hidden" onChange={(e) => setComprovante(e.target.files[0])} />
                    </div>

                    {/* Botão de Envio */}
                    <button
                        type="submit"
                        disabled={isLoading}
                        className="w-full font-bold text-lg text-white bg-gradient-to-r from-blue-600 to-indigo-600 p-4 rounded-lg shadow-lg hover:scale-105 transition transform duration-300 disabled:bg-slate-600 disabled:hover:scale-100 disabled:cursor-not-allowed"
                    >
                        {isLoading ? 'Processando...' : 'Juntar e Baixar PDF'}
                    </button>
                </form>

                {/* Mensagens de Status */}
                {error && <p className="text-red-400 font-semibold mt-4">{error}</p>}
                {success && <p className="text-green-500 font-semibold mt-4">{success}</p>}
            </div>
        </div>
    );
}

export default App;