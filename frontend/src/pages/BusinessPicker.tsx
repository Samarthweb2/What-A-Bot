const MOCK_DATA = import.meta.env.DEV ? { businesses: [] } : null;

export default function BusinessPicker() {
  console.log(MOCK_DATA);
  return <div>Business Picker Page</div>;
}
