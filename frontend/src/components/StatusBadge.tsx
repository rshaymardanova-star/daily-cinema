const STATUS_COLORS: Record<string, string> = {
  created: "bg-gray-100 text-gray-700",
  pending: "bg-yellow-100 text-yellow-800",
  processing: "bg-blue-100 text-blue-800",
  rendering: "bg-indigo-100 text-indigo-800",
  completed: "bg-green-100 text-green-800",
  failed: "bg-red-100 text-red-800",
  queued: "bg-purple-100 text-purple-800",
  not_found: "bg-gray-100 text-gray-500",
};

export default function StatusBadge({ status }: { status: string }) {
  const color = STATUS_COLORS[status] ?? "bg-gray-100 text-gray-600";
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${color}`}
    >
      {status}
    </span>
  );
}
