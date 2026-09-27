// MOCK data restricted to DEV mode
const MOCK_DATA = import.meta.env.DEV ? { isDev: true } : null;

export default function Login() {
  console.log(MOCK_DATA);
  return <div>Login Page</div>;
}
