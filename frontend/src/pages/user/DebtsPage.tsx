import React, { useEffect, useState } from "react";
import {
  listMyDebts,
  listCreatedDebts,
  payDebt,
  confirmDebt,
  markDebtUnpaid,
  type Debt,
} from "./services/DebtsService";
import CreateDebtModal from "./components/CreateDebtModal";

type FilterType = "all" | "paid" | "unpaid" | "confirmed" | "unconfirmed";

const DebtsPage: React.FC = () => {
  const [myDebts, setMyDebts] = useState<Debt[]>([]);
  const [createdDebts, setCreatedDebts] = useState<Debt[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [myFilter, setMyFilter] = useState<FilterType>("all");
  const [createdFilter, setCreatedFilter] = useState<FilterType>("all");

  const [modalOpen, setModalOpen] = useState(false);

  const handleDebtCreated = () => {
    fetchDebts();
  };

  const fetchDebts = async () => {
    setLoading(true);
    setError(null);
    try {
      // Fetch with query params for paid/confirmed
      let myPromise: Promise<Debt[]>;
      let createdPromise: Promise<Debt[]>;

      if (myFilter === "paid") {
        myPromise = listMyDebts(true);
      } else if (myFilter === "unpaid") {
        myPromise = listMyDebts(false);
      } else {
        myPromise = listMyDebts();
      }

      if (createdFilter === "confirmed") {
        createdPromise = listCreatedDebts(true);
      } else if (createdFilter === "unconfirmed") {
        createdPromise = listCreatedDebts(false);
      } else {
        createdPromise = listCreatedDebts();
      }

      const [my, created] = await Promise.all([myPromise, createdPromise]);
      setMyDebts(my);
      setCreatedDebts(created);
    } catch (err) {
      setError("Could not load debts.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDebts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [myFilter, createdFilter]);

  const handlePay = async (id: number) => {
    try {
      await payDebt(id);
      fetchDebts();
    } catch {
      alert("Could not pay debt.");
    }
  };

  const handleConfirm = async (id: number) => {
    try {
      await confirmDebt(id);
      fetchDebts();
    } catch {
      alert("Could not confirm debt.");
    }
  };

  const handleMarkUnpaid = async (id: number) => {
    try {
      await markDebtUnpaid(id);
      fetchDebts();
    } catch {
      alert("Could not mark debt as unpaid.");
    }
  };

  return (
    <div className="container mx-auto px-4">
      {/* Modern floating button above lists */}
      <div className="flex justify-end mb-8">
        <button
          className="flex items-center gap-2 px-5 py-2 rounded-full bg-gradient-to-r from-blue-600 to-blue-400 text-white font-semibold shadow-lg hover:scale-105 hover:from-blue-700 hover:to-blue-500 transition-all duration-150"
          onClick={() => setModalOpen(true)}
        >
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            strokeWidth={2}
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
          </svg>
          Create Debt
        </button>
      </div>
      <CreateDebtModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onCreated={handleDebtCreated}
      />
      {loading ? (
        <div className="flex justify-center items-center py-16">
          <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-blue-600 border-opacity-50"></div>
        </div>
      ) : error ? (
        <div className="text-center text-red-600 py-8">{error}</div>
      ) : (
        <div className="flex flex-col md:flex-row gap-8">
          {/* My Debts */}
          <div className="flex-1 bg-white rounded-2xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-blue-600 flex items-center gap-2">
                <span className="inline-block w-2 h-2 bg-blue-600 rounded-full"></span>
                My Debts
              </h2>
              <div className="flex gap-2">
                <button
                  className={`px-3 py-1 rounded-full text-xs ${
                    myFilter === "all"
                      ? "bg-blue-600 text-white"
                      : "bg-gray-100 text-blue-700"
                  }`}
                  onClick={() => setMyFilter("all")}
                >
                  All
                </button>
                <button
                  className={`px-3 py-1 rounded-full text-xs ${
                    myFilter === "paid"
                      ? "bg-blue-600 text-white"
                      : "bg-gray-100 text-blue-700"
                  }`}
                  onClick={() => setMyFilter("paid")}
                >
                  Paid
                </button>
                <button
                  className={`px-3 py-1 rounded-full text-xs ${
                    myFilter === "unpaid"
                      ? "bg-blue-600 text-white"
                      : "bg-gray-100 text-blue-700"
                  }`}
                  onClick={() => setMyFilter("unpaid")}
                >
                  Unpaid
                </button>
              </div>
            </div>
            {myDebts.length === 0 ? (
              <div className="text-gray-500 text-center py-8">
                No debts found.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-blue-50">
                      <th className="py-3 px-4 font-medium text-left">Type</th>
                      <th className="py-3 px-4 font-medium text-left">
                        Amount
                      </th>
                      <th className="py-3 px-4 font-medium text-left">
                        Description
                      </th>
                      <th className="py-3 px-4 font-medium text-center">
                        Paid
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {myDebts.map((debt) => (
                      <tr
                        key={debt.id}
                        className="border-t hover:bg-blue-50 transition"
                      >
                        <td className="py-2 px-4">{debt.type}</td>
                        <td className="py-2 px-4">{debt.amount}</td>
                        <td className="py-2 px-4">{debt.description}</td>
                        <td className="py-2 px-4 text-center">
                          {debt.is_paid ? (
                            <span className="inline-block px-2 py-1 rounded bg-green-100 text-green-700 font-semibold text-xs">
                              Paid
                            </span>
                          ) : (
                            <button
                              className="bg-blue-600 text-white px-4 py-1 rounded-full hover:bg-blue-700 transition font-medium text-xs"
                              onClick={() => handlePay(debt.id)}
                            >
                              Pay
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
          {/* Created Debts */}
          <div className="flex-1 bg-white rounded-2xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-blue-600 flex items-center gap-2">
                <span className="inline-block w-2 h-2 bg-blue-600 rounded-full"></span>
                Created Debts
              </h2>
              <div className="flex gap-2">
                <button
                  className={`px-3 py-1 rounded-full text-xs ${
                    createdFilter === "all"
                      ? "bg-blue-600 text-white"
                      : "bg-gray-100 text-blue-700"
                  }`}
                  onClick={() => setCreatedFilter("all")}
                >
                  All
                </button>
                <button
                  className={`px-3 py-1 rounded-full text-xs ${
                    createdFilter === "confirmed"
                      ? "bg-blue-600 text-white"
                      : "bg-gray-100 text-blue-700"
                  }`}
                  onClick={() => setCreatedFilter("confirmed")}
                >
                  Confirmed
                </button>
                <button
                  className={`px-3 py-1 rounded-full text-xs ${
                    createdFilter === "unconfirmed"
                      ? "bg-blue-600 text-white"
                      : "bg-gray-100 text-blue-700"
                  }`}
                  onClick={() => setCreatedFilter("unconfirmed")}
                >
                  Unconfirmed
                </button>
              </div>
            </div>
            {createdDebts.length === 0 ? (
              <div className="text-gray-500 text-center py-8">
                No debts found.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-blue-50">
                      <th className="py-3 px-4 font-medium text-left">Type</th>
                      <th className="py-3 px-4 font-medium text-left">
                        Amount
                      </th>
                      <th className="py-3 px-4 font-medium text-left">
                        Description
                      </th>
                      <th className="py-3 px-4 font-medium text-center">
                        Paid
                      </th>
                      <th className="py-3 px-4 font-medium text-center">
                        Confirmed
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {createdDebts.map((debt) => (
                      <tr
                        key={debt.id}
                        className="border-t hover:bg-blue-50 transition"
                      >
                        <td className="py-2 px-4">{debt.type}</td>
                        <td className="py-2 px-4">{debt.amount}</td>
                        <td className="py-2 px-4">{debt.description}</td>
                        <td className="py-2 px-4 text-center">
                          {debt.is_paid ? (
                            <button
                              className="inline-block px-2 py-1 rounded bg-green-100 text-green-700 font-semibold text-xs hover:bg-red-100 hover:text-red-700 transition"
                              onClick={() => handleMarkUnpaid(debt.id)}
                              title="Mark as unpaid"
                            >
                              Paid
                            </button>
                          ) : (
                            <span className="inline-block px-2 py-1 rounded bg-gray-100 text-gray-500 font-semibold text-xs">
                              Not paid
                            </span>
                          )}
                        </td>
                        <td className="py-2 px-4 text-center">
                          {debt.is_confirmed ? (
                            <span className="inline-block px-2 py-1 rounded bg-green-100 text-green-700 font-semibold text-xs">
                              Confirmed
                            </span>
                          ) : debt.is_paid ? (
                            <button
                              className="bg-green-600 text-white px-4 py-1 rounded-full hover:bg-green-700 transition font-medium text-xs"
                              onClick={() => handleConfirm(debt.id)}
                            >
                              Confirm
                            </button>
                          ) : (
                            <span className="inline-block px-2 py-1 rounded bg-gray-100 text-gray-500 font-semibold text-xs">
                              Not confirmed
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default DebtsPage;
