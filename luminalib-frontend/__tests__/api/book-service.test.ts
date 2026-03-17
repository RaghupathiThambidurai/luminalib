import { bookService } from "../../api/book-service";
import { apiClient } from "@/lib/api-client";

jest.mock("@/lib/api-client");

const mockedApi = apiClient as jest.Mocked<typeof apiClient>;

describe("bookService", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("getBooks calls apiClient.request with correct URL + method", async () => {
    mockedApi.request.mockResolvedValueOnce({ books: [], total: 0 } as any);

    await bookService.getBooks(0, 10);

    expect(mockedApi.request).toHaveBeenCalledWith(
      "/api/books?skip=0&limit=10",
      { method: "GET" }
    );
  });

  it("getBooks clamps limit to 100", async () => {
    mockedApi.request.mockResolvedValueOnce({ books: [], total: 0 } as any);

    await bookService.getBooks(0, 999);

    expect(mockedApi.request).toHaveBeenCalledWith(
      "/api/books?skip=0&limit=100",
      { method: "GET" }
    );
  });

  it("getBook calls correct endpoint", async () => {
    mockedApi.request.mockResolvedValueOnce({ id: "123" } as any);

    await bookService.getBook("123");

    expect(mockedApi.request).toHaveBeenCalledWith("/api/books/123", {
      method: "GET",
    });
  });

  it("searchBooks encodes query and calls correct endpoint", async () => {
    mockedApi.request.mockResolvedValueOnce({ books: [], total: 0 } as any);

    await bookService.searchBooks("Stephen King", 5, 10);

    expect(mockedApi.request).toHaveBeenCalledWith(
      "/api/books/search/Stephen%20King?skip=5&limit=10",
      { method: "GET" }
    );
  });

  it("createBook uses uploadFile with FormData", async () => {
    mockedApi.uploadFile.mockResolvedValueOnce({ id: "new" } as any);

    await bookService.createBook({ title: "T", author: "A" } as any);

    expect(mockedApi.uploadFile).toHaveBeenCalledWith(
      "/api/books/",
      expect.any(FormData)
    );
  });

  it("updateBook sends PUT with body", async () => {
    mockedApi.request.mockResolvedValueOnce({ id: "1", title: "U" } as any);

    await bookService.updateBook("1", { title: "U" } as any);

    expect(mockedApi.request).toHaveBeenCalledWith("/api/books/1", {
      method: "PUT",
      body: { title: "U" },
    });
  });

  it("deleteBook sends DELETE", async () => {
    mockedApi.request.mockResolvedValueOnce(undefined as any);

    await bookService.deleteBook("1");

    expect(mockedApi.request).toHaveBeenCalledWith("/api/books/1", {
      method: "DELETE",
    });
  });

  it("borrowBook sends POST with due_date_days", async () => {
    mockedApi.request.mockResolvedValueOnce({
      borrow_id: "b1",
      status: "active",
      due_date: "2026-04-01",
    } as any);

    await bookService.borrowBook("1", 21);

    expect(mockedApi.request).toHaveBeenCalledWith("/api/books/1/borrow", {
      method: "POST",
      body: { due_date_days: 21 },
    });
  });

  it("returnBook sends POST", async () => {
    mockedApi.request.mockResolvedValueOnce({ status: "returned" } as any);

    await bookService.returnBook("1");

    expect(mockedApi.request).toHaveBeenCalledWith("/api/books/1/return", {
      method: "POST",
    });
  });

  it("propagates apiClient errors", async () => {
    mockedApi.request.mockRejectedValueOnce(new Error("API error"));

    await expect(bookService.getBooks()).rejects.toThrow("API error");
  });
});