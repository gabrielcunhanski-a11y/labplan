import { useState } from 'react';

export default function App() {
  const [vista, setVista] = useState('login');
  const [usuarios, setUsuarios] = useState([]);
  const [form, setForm] = useState({ email: '', senha: '', codigo: '' });

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const api = async (endpoint, method = 'GET', body = null) => {
    const res = await fetch(`http://127.0.0.1:5000${endpoint}`, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : null
    });
    return res.json();
  };

  const logar = async (e) => {
    e.preventDefault();
    const res = await api('/login', 'POST', form);
    if (res.sucesso) { setVista('painel'); carregar(); } else alert(res.mensagem);
  };

  const cadastrar = async (e) => {
    e.preventDefault();
    const res = await api('/usuarios', 'POST', form);
    alert(res.mensagem); if (res.sucesso) setVista('login');
  };

  const carregar = async () => setUsuarios(await api('/usuarios'));

  return (
    <div style={{ maxWidth: '500px', margin: '50px auto', fontFamily: 'sans-serif' }}>
      <h2 style={{ textAlign: 'center' }}>LABPLAN 🤖</h2>

      {vista === 'login' && (
        <form onSubmit={logar} style={{ display: 'flex', flexDirection: 'column', gap: '10px', background: '#f4f4f4', padding: '20px', borderRadius: '10px' }}>
          <h3>Login</h3>
          <input name="email" type="email" placeholder="Seu Email" onChange={handleChange} required style={{ padding: '10px' }} />
          <input name="senha" type="password" placeholder="Palavra-passe" onChange={handleChange} required style={{ padding: '10px' }} />
          <button type="submit" style={{ padding: '10px', background: '#007bff', color: '#fff', border: 'none', borderRadius: '5px' }}>Entrar</button>
          <button type="button" onClick={() => setVista('cadastro')} style={{ background: 'none', border: 'none', color: 'blue', cursor: 'pointer' }}>Criar nova conta</button>
          <button type="button" onClick={() => setVista('recuperar')} style={{ background: 'none', border: 'none', color: 'gray', cursor: 'pointer' }}>Esqueci a senha</button>
        </form>
      )}

      {vista === 'cadastro' && (
        <form onSubmit={cadastrar} style={{ display: 'flex', flexDirection: 'column', gap: '10px', background: '#e8f5e9', padding: '20px', borderRadius: '10px' }}>
          <h3>Registar (Protegido por Argon2)</h3>
          <input name="email" type="email" placeholder="Email" onChange={handleChange} required style={{ padding: '10px' }} />
          <input name="senha" type="password" placeholder="Crie uma senha" onChange={handleChange} required style={{ padding: '10px' }} />
          <button type="submit" style={{ padding: '10px', background: '#28a745', color: '#fff', border: 'none', borderRadius: '5px' }}>Finalizar Cadastro</button>
          <button type="button" onClick={() => setVista('login')} style={{ background: 'none', border: 'none', color: 'gray', cursor: 'pointer' }}>Voltar</button>
        </form>
      )}

      {vista === 'recuperar' && (
        <form style={{ display: 'flex', flexDirection: 'column', gap: '10px', background: '#fff3cd', padding: '20px', borderRadius: '10px' }}>
          <h3>Recuperar Senha</h3>
          <input name="email" type="email" placeholder="Digite seu Email" onChange={handleChange} required style={{ padding: '10px' }} />
          <button type="button" onClick={() => alert('Código enviado ao terminal!')} style={{ padding: '10px', background: '#ffc107', border: 'none', borderRadius: '5px' }}>Enviar Código</button>
          <button type="button" onClick={() => setVista('login')} style={{ background: 'none', border: 'none', color: 'gray', cursor: 'pointer' }}>Voltar ao Login</button>
        </form>
      )}

      {vista === 'painel' && (
        <div style={{ padding: '20px', background: '#fff', border: '1px solid #ddd', borderRadius: '10px' }}>
          <h3>Bem-vindo ao Painel!</h3>
          <p>Utilizadores no Sistema:</p>
          <ul>{usuarios.map(u => <li key={u.id}>{u.email}</li>)}</ul>
          <button onClick={() => setVista('login')} style={{ padding: '10px', width: '100%', background: '#dc3545', color: '#fff', border: 'none', borderRadius: '5px' }}>Sair</button>
        </div>
      )}
    </div>
  );
}