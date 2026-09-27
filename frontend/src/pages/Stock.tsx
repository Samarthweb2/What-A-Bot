const MOCK_DATA = import.meta.env.DEV ? { stock: [] } : null;

export default function Stock() {
  console.log(MOCK_DATA);
  return <div>Stock Page</div>;
}
