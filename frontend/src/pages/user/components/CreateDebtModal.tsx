import React, { useState, useEffect, useRef } from "react";
import { createDebt, listUsers, getCurrentUser, type Debt } from "../services/DebtsService";

type User = {
  id: number;
  name: string;
};

type Props = {
  open: boolean;
  onClose: () => void;
  onCreated: (debt: Debt) => void;
};

const DEBT_TYPES = [
  { value: "fuel", label: "Fuel" },
  { value: "money", label: "Money" },
  { value: "bottles", label: "Bottles" },
];

const CreateDebtModal: React.FC<Props> = ({ open, onClose, onCreated }) => {
  const [type, setType] = useState(DEBT_TYPES[0].value);
  const [amount, setAmount] = useState<number>(0);
  const [description, setDescription] = useState("");
  const [debtee, setDebtee] = useState<User | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const [currentUserId, setCurrentUserId] = useState<number | null>(null);

  useEffect(() => {
    if (!open) return;
    let currentUserId: number | null;
    getCurrentUser()
      .then(user => {
        currentUserId = user.id;
        return listUsers();
      })
      .then(data => {
        setUsers(currentUserId ? data.filter(u => u.id !== currentUserId) : data);
        setCurrentUserId(currentUserId);
      })
      .catch(() => setUsers([]));
  }, [open]);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setDropdownOpen(false);
      }
    }
    if (dropdownOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [dropdownOpen]);

  const filteredUsers = users.filter(user =>
    user.name.toLowerCase().includes(search.toLowerCase())
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    if (!debtee) {
      setError("Please select a debtee.");
      setLoading(false);
      return;
    }
    try {
      const debt = await createDebt({ type, amount, description, is_paid: false, is_confirmed: false, owner: currentUserId ?? undefined, debtee: debtee.id });
      onCreated(debt);
      onClose();
    } catch {
      setError("Failed to create debt");
    } finally {
      setLoading(false);
    }
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 flex items-center justify-center z-50 backdrop-blur-md bg-black/10">
      <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md border border-blue-100 relative animate-fade-in">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-blue-600 transition"
          aria-label="Close"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
        <h2 className="text-2xl font-extrabold mb-6 text-blue-700 text-center tracking-tight">
          Create Debt
        </h2>
        {error && <div className="mb-2 text-red-600 text-center">{error}</div>}
        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block mb-1 text-gray-700 font-medium">Type</label>
            <select
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-300 bg-gray-50"
              value={type}
              onChange={e => setType(e.target.value)}
              required
            >
              {DEBT_TYPES.map(dt => (
                <option key={dt.value} value={dt.value}>{dt.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block mb-1 text-gray-700 font-medium">Amount</label>
            <input
              type="number"
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-300 bg-gray-50"
              value={amount}
              onChange={e => setAmount(Number(e.target.value))}
              required
              min={0}
              placeholder="Enter amount"
            />
          </div>
          <div>
            <label className="block mb-1 text-gray-700 font-medium">Description</label>
            <input
              type="text"
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-300 bg-gray-50"
              value={description}
              onChange={e => setDescription(e.target.value)}
              placeholder="Optional description"
            />
          </div>
          <div>
            <label className="block mb-1 text-gray-700 font-medium">Debtee</label>
            <div className="relative" ref={dropdownRef}>
              <input
                type="text"
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-300 bg-gray-50"
                placeholder="Search user..."
                value={debtee ? debtee.name : search}
                onChange={e => {
                  setSearch(e.target.value);
                  setDebtee(null);
                  setDropdownOpen(true);
                }}
                onFocus={() => setDropdownOpen(true)}
                autoComplete="off"
              />
              {dropdownOpen && (
                <ul className="absolute z-10 w-full bg-white border border-blue-100 rounded-lg mt-1 max-h-48 overflow-y-auto shadow-lg">
                  {filteredUsers.length === 0 && (
                    <li className="px-3 py-2 text-gray-400">No users found</li>
                  )}
                  {filteredUsers.map(user => (
                    <li
                      key={user.id}
                      className={`px-3 py-2 cursor-pointer hover:bg-blue-100 ${
                        debtee?.id === user.id ? "bg-blue-50 font-semibold" : ""
                      }`}
                      onClick={() => {
                        setDebtee(user);
                        setSearch("");
                        setDropdownOpen(false);
                      }}
                    >
                      {user.name}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              className="px-4 py-2 rounded-full bg-gray-100 text-gray-700 hover:bg-gray-200 transition font-semibold"
              onClick={onClose}
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 rounded-full bg-gradient-to-r from-blue-600 to-blue-400 text-white hover:from-blue-700 hover:to-blue-500 font-semibold shadow-lg transition-all duration-150"
              disabled={loading}
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <span className="animate-spin w-4 h-4 border-t-2 border-white rounded-full"></span>
                  Creating...
                </span>
              ) : (
                "Create"
              )}
            </button>
          </div>
        </form>
      </div>
      <style>
        {`
          .animate-fade-in {
            animation: fadeIn 0.25s ease;
          }
          @keyframes fadeIn {
            from { opacity: 0; transform: scale(0.95);}
            to { opacity: 1; transform: scale(1);}
          }
        `}
      </style>
    </div>
  );
};

export default CreateDebtModal;